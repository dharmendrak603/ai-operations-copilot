
import time

from agents.planner_agent import PlannerAgent
from agents.analyst_agent import AnalystAgent
from agents.reviewer_agent import ReviewerAgent
from agents.executor_agent import ExecutorAgent

from database.db_manager import DatabaseManager

from logs.logger import WorkflowLogger

from tools.data_tools import DataTools


class WorkflowManager:

    def __init__(self):

        self.planner_agent = PlannerAgent()

        self.analyst_agent = AnalystAgent()

        self.reviewer_agent = ReviewerAgent()

        self.executor_agent = ExecutorAgent()

        self.db_manager = DatabaseManager()

        self.max_retries = 2

    # =====================================================
    # MAIN WORKFLOW
    # =====================================================

    def execute_workflow(
        self,
        user_input,
        uploaded_df=None,
        data_profile=None,
        summary_stats=None
    ):

        workflow_id = int(
            time.time() * 1000
        )

        WorkflowLogger.log_workflow_started(
            workflow_id
        )

        # =================================================
        # ANALYTICS ENGINE
        # =================================================

        analysis_results = None

        if uploaded_df is not None:

            try:

                analysis_results = (
                    DataTools.run_analysis(
                        uploaded_df
                    )
                )

            except Exception as e:

                WorkflowLogger.error(
                    f"Analytics Engine Error: {e}"
                )

                analysis_results = {
                    "status": "error",
                    "message": str(e)
                }

        # =================================================
        # DATA CONTEXT
        # =================================================

        data_context = ""

        if data_profile:

            data_context = f"""

DATASET PROFILE
----------------

Rows:
{data_profile['rows']}

Columns:
{data_profile['columns']}

Column Names:
{data_profile['column_names']}

Missing Values:
{data_profile['missing_values']}

Data Types:
{data_profile['data_types']}

SUMMARY STATISTICS
------------------

{summary_stats}

REAL_ANALYTICS_RESULTS
----------------------

{analysis_results}
"""

        # =================================================
        # PLANNER AGENT
        # =================================================

        planner_prompt = f"""

You are a Workflow Planning Agent.

USER REQUEST:
{user_input}

DATA CONTEXT:
{data_context}

YOUR RESPONSIBILITIES:
- Understand user intent
- Identify analytical objectives
- Identify potential risks
- Create structured execution plan
- Determine what insights should be generated

Keep response concise and structured.
"""

        planner_response = (
            self.planner_agent.chat(
                planner_prompt
            )
        )

        WorkflowLogger.log_agent_completed(
            "Planner Agent",
            workflow_id
        )

        # =================================================
        # ANALYST AGENT
        # =================================================

        analyst_prompt = f"""

You are a Senior Enterprise AI Data Analyst.

USER REQUEST:
{user_input}

PLANNER OUTPUT:
{planner_response}

DATA CONTEXT:
{data_context}

IMPORTANT RULES:
- Use REAL_ANALYTICS_RESULTS as the source of truth
- NEVER invent KPI values
- NEVER hallucinate metrics
- Use concise executive formatting
- Prefer bullet points
- Mention trends, anomalies, and risks
- Focus on business value
- Mention data quality concerns when relevant

RESPONSE FORMAT:

EXECUTIVE SUMMARY
- concise overview

KPI HIGHLIGHTS
- metric 1
- metric 2
- metric 3

KEY INSIGHTS
- insight 1
- insight 2

DATA QUALITY ISSUES
- issue 1
- issue 2

RISKS
- risk 1
- risk 2

RECOMMENDATIONS
- recommendation 1
- recommendation 2
"""

        analyst_response = (
            self.analyst_agent.chat(
                analyst_prompt
            )
        )

        WorkflowLogger.log_agent_completed(
            "Analyst Agent",
            workflow_id
        )

        # =================================================
        # REVIEWER AGENT
        # =================================================

        reviewer_prompt = f"""

You are an AI Governance and Quality Reviewer.

USER REQUEST:
{user_input}

ANALYST RESPONSE:
{analyst_response}

YOUR RESPONSIBILITIES:
- Detect hallucinations
- Detect weak analytical logic
- Detect governance concerns
- Detect unsupported claims
- Evaluate business risk
- Evaluate data quality awareness

RETURN:
- approval decision
- risk level
- reviewer comments
"""

        reviewer_response = (
            self.reviewer_agent.chat(
                reviewer_prompt
            )
        )

        WorkflowLogger.log_agent_completed(
            "Reviewer Agent",
            workflow_id
        )

        # =================================================
        # REVIEW PARSING
        # =================================================

        approval_status = "approved"

        risk_level = "low"

        review_text = str(
            reviewer_response
        ).lower()

        if "medium" in review_text:

            risk_level = "medium"

        if "high" in review_text:

            risk_level = "high"

        if (
            "reject" in review_text
            or
            "rejected" in review_text
        ):

            approval_status = "rejected"

        WorkflowLogger.info(

            f"Reviewer Decision: "
            f"{approval_status} | "
            f"Risk Level: {risk_level}"
        )

        # =================================================
        # WORKFLOW STATE
        # =================================================

        workflow_state = {

            "workflow_id": workflow_id,

            "user_input": user_input,

            "workflow_status": "review_completed",

            "approval_status": approval_status,

            "human_approval": "pending",

            "execution_status": "pending",

            "risk_level": risk_level,

            "planner_response": planner_response,

            "analyst_response": analyst_response,

            "reviewer_response": reviewer_response,

            "executor_response": None
        }

        return workflow_state

    # =====================================================
    # EXECUTE APPROVED WORKFLOW
    # =====================================================

    def execute_approved_workflow(
        self,
        workflow_state
    ):

        workflow_id = (
            workflow_state["workflow_id"]
        )

        # ================================================
        # HUMAN REJECTION
        # ================================================

        if (
            workflow_state["human_approval"]
            == "rejected"
        ):

            workflow_state[
                "execution_status"
            ] = "blocked"

            workflow_state[
                "workflow_status"
            ] = "completed"

            workflow_state[
                "executor_response"
            ] = {
                "status": "blocked",
                "reason": (
                    "Human rejected execution."
                )
            }

            WorkflowLogger.log_human_rejected(
                workflow_id
            )

            WorkflowLogger.log_workflow_completed(
                workflow_id
            )

            self.db_manager.save_workflow(
                workflow_state
            )

            return workflow_state

        # ================================================
        # EXECUTOR AGENT
        # ================================================

        executor_prompt = f"""

Execute approved workflow.

USER REQUEST:
{workflow_state['user_input']}

PLANNER OUTPUT:
{workflow_state['planner_response']}

ANALYST OUTPUT:
{workflow_state['analyst_response']}

Generate concise execution summary.
"""

        executor_response = (
            self.executor_agent.chat(
                executor_prompt
            )
        )

        # ================================================
        # UPDATE STATE
        # ================================================

        workflow_state[
            "executor_response"
        ] = executor_response

        workflow_state[
            "execution_status"
        ] = "executed"

        workflow_state[
            "workflow_status"
        ] = "completed"

        WorkflowLogger.log_execution_completed(
            workflow_id
        )

        WorkflowLogger.log_workflow_completed(
            workflow_id
        )

        # ================================================
        # SAVE DATABASE
        # ================================================

        self.db_manager.save_workflow(
            workflow_state
        )

        return workflow_state
