from agents.planner_agent import PlannerAgent
from agents.analyst_agent import AnalystAgent
from agents.reviewer_agent import ReviewerAgent
from agents.executor_agent import ExecutorAgent
from logs.logger import WorkflowLogger
import json
from database.db_manager import DatabaseManager


class WorkflowManager:

    def __init__(self):

        self.planner_agent = PlannerAgent()

        self.analyst_agent = AnalystAgent()

        self.reviewer_agent = ReviewerAgent()

        self.executor_agent = ExecutorAgent()

        self.db_manager = DatabaseManager()
        self.max_retries = 3
        

    def execute_workflow(self, user_input):

        workflow_state = {

            "workflow_id": id(user_input),

            "workflow_status": "started",

            "approval_status": "pending",

            "human_approval": "pending",

            "execution_status": "pending",

            "risk_level": "unknown",

            "user_input": user_input,

            "planner_response": None,

            "analyst_response": None,

            "reviewer_response": None,

            "executor_response": None
        }
        WorkflowLogger.log(
            f"Workflow Started | ID: {workflow_state['workflow_id']}"
        )
        # =========================================================
        # STEP 1 — Planner Agent
        # =========================================================

        planner_response = self.planner_agent.chat(user_input)

        workflow_state["planner_response"] = planner_response

        workflow_state["workflow_status"] = "planning_completed"
        WorkflowLogger.log(
            f"Planner Agent Completed | Workflow ID: {workflow_state['workflow_id']}"
        )

        # =========================================================
        # STEP 2 — Analyst Agent
        # =========================================================

        analyst_input = f"""
        User Request:
        {user_input}

        Planner Response:
        {planner_response}
        """

        analyst_response = self.analyst_agent.chat(analyst_input)

        workflow_state["analyst_response"] = analyst_response

        workflow_state["workflow_status"] = "analysis_completed"
        WorkflowLogger.log(
            f"Analyst Agent Completed | Workflow ID: {workflow_state['workflow_id']}"
        )
        # =========================================================
        # STEP 3 — Reviewer Agent
        # =========================================================

        reviewer_input = f"""
        User Request:
        {user_input}

        Planner Response:
        {planner_response}

        Analyst Response:
        {analyst_response}

        Review the overall quality, risks, and completeness.
        """

        reviewer_response = self.reviewer_agent.chat(reviewer_input)

        workflow_state["workflow_status"] = "review_completed"
        WorkflowLogger.log(
            f"Reviewer Agent Completed | Workflow ID: {workflow_state['workflow_id']}"
        )
        # =========================================================
        # VALIDATE & PARSE REVIEWER OUTPUT
        # =========================================================

        reviewer_output = None

        for attempt in range(self.max_retries):

            try:

                reviewer_output = reviewer_response.get("response", {})

                if isinstance(reviewer_output, str):

                    reviewer_output = json.loads(reviewer_output)

                WorkflowLogger.log(
                    f"Reviewer Output Parsed Successfully | Attempt: {attempt + 1}"
                )

                break

            except Exception as error:

                WorkflowLogger.log(
                    f"Reviewer Parsing Failed | Attempt: {attempt + 1} | Error: {error}"
                )

                # Retry reviewer agent

                reviewer_response = self.reviewer_agent.chat(
                    reviewer_input
                )

        # FINAL FAILSAFE

        if reviewer_output is None:

            reviewer_output = {
                "approval_decision": "rejected",
                "risk_level": "high",
                "missing_considerations": [
                    "Reviewer response parsing failed after retries"
                ],
                "summary": "Workflow automatically rejected due to invalid reviewer output."
            }

        # STORE STRUCTURED REVIEWER OUTPUT

        workflow_state["reviewer_response"] = reviewer_output

        # UPDATE WORKFLOW STATE

        workflow_state["approval_status"] = reviewer_output.get(
            "approval_decision",
            "rejected"
        )

        workflow_state["risk_level"] = reviewer_output.get(
            "risk_level",
            "high"
        )
        WorkflowLogger.log(
            f"Reviewer Decision: {workflow_state['approval_status']} | "
            f"Risk Level: {workflow_state['risk_level']}"
        )
        # =========================================================
        # STEP 4 — HUMAN APPROVAL
        # =========================================================

        if workflow_state["approval_status"] == "approved":



            human_decision = input(
                "\nHuman Approval Required. Approve execution? (yes/no): "
            ).strip().lower()

            if human_decision == "yes":

                workflow_state["human_approval"] = "approved"
                WorkflowLogger.log(
                    f"Human Approved Execution | Workflow ID: {workflow_state['workflow_id']}"
                )

            else:

                workflow_state["human_approval"] = "rejected"
                WorkflowLogger.log(
                    f"Human Rejected Execution | Workflow ID: {workflow_state['workflow_id']}"
                )

        else:

            workflow_state["human_approval"] = "rejected"

        # =========================================================
        # STEP 5 — Executor Agent
        # =========================================================

        if (
            workflow_state["approval_status"] == "approved"
            and workflow_state["human_approval"] == "approved"
        ):

            executor_input = f"""
            User Request:
            {user_input}

            Planner Response:
            {planner_response}

            Analyst Response:
            {analyst_response}

            Reviewer Response:
            {reviewer_output}

            Simulate execution of the approved task.
            """

            executor_response = self.executor_agent.chat(executor_input)

            # =====================================================
            # VALIDATE & PARSE EXECUTOR OUTPUT
            # =====================================================

            executor_output = executor_response.get("response", {})

            if isinstance(executor_output, str):

                try:

                    executor_output = json.loads(executor_output)

                except Exception:

                    executor_output = {
                        "execution_status": "failed",
                        "execution_summary": "Executor output parsing failed."
                    }

            workflow_state["executor_response"] = executor_output

            workflow_state["execution_status"] = executor_output.get(
                "execution_status",
                "executed"
            )
            WorkflowLogger.log(
                f"Execution Completed | Workflow ID: {workflow_state['workflow_id']}"
            )
        else:

            workflow_state["executor_response"] = {
                "execution_status": "not_executed",
                "execution_summary": (
                    "Execution did not run due to reviewer rejection "
                    "or missing human approval."
                )
            }

            workflow_state["execution_status"] = "blocked"
            WorkflowLogger.log(
                f"Execution Blocked | Workflow ID: {workflow_state['workflow_id']}"
            )

        # =========================================================
        # FINAL WORKFLOW STATUS
        # =========================================================

        workflow_state["workflow_status"] = "completed"

        WorkflowLogger.log(
            f"Workflow Completed | ID: {workflow_state['workflow_id']}"
        )
        self.db_manager.save_workflow(workflow_state)   
        return workflow_state