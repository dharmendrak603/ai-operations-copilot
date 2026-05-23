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


    # -----------------------------------
    # MAIN WORKFLOW
    # -----------------------------------

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


        # -----------------------------------
        # ADVANCED ANALYTICS
        # -----------------------------------

        top_products = None

        missing_analysis = None

        correlation_analysis = None

        sales_trend_analysis = None


        if uploaded_df is not None:

            try:

                top_products = (
                    DataTools.top_products_analysis(
                        uploaded_df
                    )
                )

                missing_analysis = (
                    DataTools.missing_value_analysis(
                        uploaded_df
                    )
                )

                correlation_analysis = (
                    DataTools.correlation_analysis(
                        uploaded_df
                    )
                )

                sales_trend_analysis = (
                    DataTools.sales_trend_analysis(
                        uploaded_df
                    )
                )

            except Exception as e:

                WorkflowLogger.error(
                    f"Analytics Error: {e}"
                )


        # -----------------------------------
        # DATA CONTEXT
        # -----------------------------------

        data_context = ""

        if data_profile:

            data_context = f"""

            Dataset Profile
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

            Summary Statistics:
            {summary_stats}

            Top Products Analysis:
            {top_products}

            Missing Value Analysis:
            {missing_analysis}

            Correlation Analysis:
            {correlation_analysis}

            Sales Trend Analysis:
            {sales_trend_analysis}
            """


        # -----------------------------------
        # PLANNER AGENT
        # -----------------------------------

        planner_prompt = f"""

        User Request:
        {user_input}

        {data_context}

        Create a structured execution plan.
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


        # -----------------------------------
        # ANALYST AGENT
        # -----------------------------------

        analyst_prompt = f"""

        You are a Senior AI Data Analyst.

        User Request:
        {user_input}

        Planner Output:
        {planner_response}

        Dataset Profile:
        {data_profile}

        Summary Statistics:
        {summary_stats}

        Top Products Analysis:
        {top_products}

        Missing Value Analysis:
        {missing_analysis}

        Correlation Analysis:
        {correlation_analysis}

        Sales Trend Analysis:
        {sales_trend_analysis}

        Generate REAL business insights,
        trends,
        patterns,
        anomalies,
        risks,
        recommendations,
        and data quality observations.

        Avoid generic explanations.
        Use the computed analytics above.
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


        # -----------------------------------
        # REVIEWER AGENT
        # -----------------------------------

        reviewer_prompt = f"""

        Review the following AI analysis.

        Analyst Output:
        {analyst_response}

        Determine:
        - approval status
        - risk level
        - governance concerns
        - quality issues
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


        # -----------------------------------
        # REVIEW PARSING
        # -----------------------------------

        approval_status = "approved"

        risk_level = "low"


        if isinstance(reviewer_response, dict):

            review_text = str(
                reviewer_response
            ).lower()

        else:

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


        # -----------------------------------
        # BUILD WORKFLOW STATE
        # -----------------------------------

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


    # -----------------------------------
    # EXECUTE APPROVED WORKFLOW
    # -----------------------------------

    def execute_approved_workflow(
        self,
        workflow_state
    ):

        workflow_id = (
            workflow_state["workflow_id"]
        )


        # -----------------------------------
        # HUMAN REJECTED
        # -----------------------------------

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


        # -----------------------------------
        # EXECUTOR AGENT
        # -----------------------------------

        executor_prompt = f"""

        Execute approved workflow.

        User Request:
        {workflow_state['user_input']}

        Planner Output:
        {workflow_state['planner_response']}

        Analyst Output:
        {workflow_state['analyst_response']}
        """

        executor_response = (
            self.executor_agent.chat(
                executor_prompt
            )
        )


        # -----------------------------------
        # UPDATE STATE
        # -----------------------------------

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


        # -----------------------------------
        # SAVE DATABASE
        # -----------------------------------

        self.db_manager.save_workflow(
            workflow_state
        )


        return workflow_state