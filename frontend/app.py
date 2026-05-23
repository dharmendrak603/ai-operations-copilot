import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

import streamlit as st
import pandas as pd
import plotly.express as px

from workflows.workflow_manager import WorkflowManager
from tools.data_tools import DataTools


# -----------------------------------
# INITIALIZE
# -----------------------------------

workflow_manager = WorkflowManager()


# -----------------------------------
# PAGE CONFIG
# -----------------------------------

st.set_page_config(
    page_title="AI Operations Copilot",
    layout="wide",
    initial_sidebar_state="expanded"
)


# -----------------------------------
# SESSION STATE
# -----------------------------------

if "workflow_result" not in st.session_state:
    st.session_state.workflow_result = None

if "workflow_input" not in st.session_state:
    st.session_state.workflow_input = ""


# -----------------------------------
# CUSTOM CSS
# -----------------------------------

st.markdown("""
<style>

.stApp {
    background-color: #0B0F19;
    color: white;
}

.main {
    background-color: #0B0F19;
    color: white;
}

html, body, [class*="css"] {
    font-family: 'Segoe UI', sans-serif;
    color: white;
}

[data-testid="stAppViewContainer"] {
    background-color: #0B0F19;
}

[data-testid="stHeader"] {
    background-color: #0B0F19;
}

section[data-testid="stSidebar"] {
    background-color: #070B12;
    border-right: 1px solid #1E293B;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 95%;
}

[data-testid="metric-container"] {
    background: linear-gradient(
        145deg,
        #111827,
        #0F172A
    );

    border: 1px solid #1E293B;

    padding: 20px;

    border-radius: 16px;

    box-shadow:
        0px 0px 20px rgba(0,0,0,0.35);

    color: white !important;
}

[data-testid="stMetricLabel"] {
    color: #CBD5E1 !important;
    font-size: 15px !important;
    font-weight: 600 !important;
}

[data-testid="stMetricValue"] {
    color: white !important;
    font-size: 28px !important;
    font-weight: bold !important;
}

.streamlit-expanderHeader {
    background-color: #111827;
    border-radius: 10px;
    border: 1px solid #1E293B;
    padding: 10px;
    color: white;
}

.stButton > button {
    width: 100%;
    border-radius: 10px;
    height: 3em;
    background-color: #111827;
    color: white;
    border: 1px solid #334155;
    font-weight: 600;
}

textarea {
    border-radius: 12px !important;
    border: 1px solid #334155 !important;
    background-color: #111827 !important;
    color: white !important;
}

textarea::placeholder {
    color: #94A3B8 !important;
}

</style>
""", unsafe_allow_html=True)


# -----------------------------------
# SIDEBAR
# -----------------------------------

history = workflow_manager.db_manager.get_workflow_history()

total_workflows = len(history)

executed_count = len([
    row for row in history
    if row[3] == "executed"
])

blocked_count = len([
    row for row in history
    if row[3] == "blocked"
])

st.sidebar.title("AI Operations Dashboard")

st.sidebar.metric(
    "Total Workflows",
    total_workflows
)

st.sidebar.metric(
    "Executed",
    executed_count
)

st.sidebar.metric(
    "Blocked",
    blocked_count
)

st.sidebar.success("Backend Services Active")


# -----------------------------------
# HEADER
# -----------------------------------

st.title("AI Operations Copilot")

st.caption(
    "Multi-Agent AI Orchestration Platform"
)


# -----------------------------------
# USER INPUT
# -----------------------------------

st.subheader("Submit Workflow Request")


# CSV UPLOADER

uploaded_file = st.file_uploader(
    "Upload CSV File",
    type=["csv"]
)


# DATA VARIABLES

df = None

data_profile = None

summary_stats = None


# LOAD CSV

if uploaded_file:

    data_result = DataTools.load_csv(
        uploaded_file
    )

    if data_result["status"] == "success":

        df = data_result["dataframe"]

        st.success(
            "CSV Uploaded Successfully"
        )

        st.subheader("Dataset Preview")

        st.dataframe(
            df.head(),
            use_container_width=True
        )

        data_profile = (
            DataTools.get_basic_profile(df)
        )

        summary_stats = (
            DataTools.get_summary_statistics(df)
        )

    else:

        st.error(
            data_result["message"]
        )


# USER PROMPT

user_input = st.text_area(
    "Enter your workflow request:",
    height=150,
    placeholder="Example: Analyze sales trends",
    key="workflow_input"
)


# -----------------------------------
# EXECUTE BUTTON
# -----------------------------------

if st.button(
    "Execute Workflow",
    use_container_width=True
):

    if user_input.strip():

        with st.spinner(
            "Executing Multi-Agent Workflow..."
        ):

            workflow_result = (
                workflow_manager.execute_workflow(
                    user_input=user_input,
                    data_profile=data_profile,
                    summary_stats=summary_stats
                )
            )

            st.session_state.workflow_result = (
                workflow_result
            )

        st.success(
            "Workflow Review Completed"
        )

    else:

        st.warning(
            "Please enter a request."
        )


# -----------------------------------
# WORKFLOW RESULT
# -----------------------------------

if st.session_state.workflow_result:

    workflow_result = (
        st.session_state.workflow_result
    )

    col1, col2 = st.columns([8, 2])

    with col2:

        if st.button("Start New Workflow"):

            st.session_state.clear()

            st.rerun()

    st.divider()

    st.header("Workflow Summary")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Workflow Status",
        workflow_result["workflow_status"]
    )

    col2.metric(
        "Approval",
        workflow_result["approval_status"]
    )

    col3.metric(
        "Execution",
        workflow_result["execution_status"]
    )

    col4.metric(
        "Risk",
        workflow_result["risk_level"]
    )


    st.markdown(
        f"### Workflow ID\n`{workflow_result['workflow_id']}`"
    )

    st.markdown(
        f"### User Request\n{workflow_result['user_input']}"
    )


    # -----------------------------------
    # AGENT OUTPUTS
    # -----------------------------------

    st.divider()

    st.header("Agent Outputs")

    with st.expander("🧠 Planner Agent"):
        st.write(
            workflow_result["planner_response"]
        )

    with st.expander("📊 Analyst Agent"):
        st.write(
            workflow_result["analyst_response"]
        )

    with st.expander("🛡 Reviewer Agent"):
        st.write(
            workflow_result["reviewer_response"]
        )


    # -----------------------------------
    # HUMAN APPROVAL
    # -----------------------------------

    if (
        workflow_result["approval_status"] == "approved"
        and workflow_result["execution_status"] == "pending"
    ):

        st.divider()

        st.header("Human Approval")

        human_decision = st.radio(
            "Approve workflow execution?",
            ["Approve", "Reject"]
        )

        if st.button("Submit Human Approval"):

            if human_decision == "Approve":

                workflow_result["human_approval"] = (
                    "approved"
                )

            else:

                workflow_result["human_approval"] = (
                    "rejected"
                )

            workflow_result = (
                workflow_manager.execute_approved_workflow(
                    workflow_result
                )
            )

            st.session_state.workflow_result = (
                workflow_result
            )

            st.rerun()


    # -----------------------------------
    # EXECUTION RESULT
    # -----------------------------------

    if workflow_result["executor_response"]:

        st.divider()

        st.header("Execution Result")

        st.success(
            f"Execution Status: "
            f"{workflow_result['execution_status']}"
        )

        st.info(
            str(
                workflow_result["executor_response"]
            )
        )


# -----------------------------------
# ANALYTICS
# -----------------------------------

st.divider()

st.header("Operational Analytics")

if history:

    history_df = pd.DataFrame(
        history,
        columns=[
            "Workflow ID",
            "Approval Status",
            "Human Approval",
            "Execution Status",
            "Risk Level",
            "Created At"
        ]
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Workflows",
        len(history_df)
    )

    col2.metric(
        "Executed",
        len(
            history_df[
                history_df["Execution Status"] == "executed"
            ]
        )
    )

    col3.metric(
        "Blocked",
        len(
            history_df[
                history_df["Execution Status"] == "blocked"
            ]
        )
    )

    approval_rate = round(
        (
            len(
                history_df[
                    history_df["Approval Status"] == "approved"
                ]
            )
            / len(history_df)
        ) * 100,
        1
    )

    col4.metric(
        "Approval Rate",
        f"{approval_rate}%"
    )


    chart_col1, chart_col2 = st.columns(2)


    # PIE CHART

    execution_counts = (
        history_df["Execution Status"]
        .value_counts()
        .reset_index()
    )

    execution_counts.columns = [
        "Execution Status",
        "Count"
    ]

    fig_pie = px.pie(
        execution_counts,
        names="Execution Status",
        values="Count",
        title="Workflow Execution Outcomes",
        hole=0.4
    )

    fig_pie.update_layout(
        paper_bgcolor="#0B0F19",
        plot_bgcolor="#0B0F19",
        font_color="white"
    )

    chart_col1.plotly_chart(
        fig_pie,
        use_container_width=True
    )


    # BAR CHART

    risk_counts = (
        history_df["Risk Level"]
        .value_counts()
        .reset_index()
    )

    risk_counts.columns = [
        "Risk Level",
        "Count"
    ]

    fig_bar = px.bar(
        risk_counts,
        x="Risk Level",
        y="Count",
        title="Risk Level Distribution"
    )

    fig_bar.update_layout(
        paper_bgcolor="#0B0F19",
        plot_bgcolor="#0B0F19",
        font_color="white"
    )

    chart_col2.plotly_chart(
        fig_bar,
        use_container_width=True
    )


    # TIMELINE

    st.subheader(
        "Workflow Activity Timeline"
    )

    timeline_df = history_df.copy()

    timeline_df["Created At"] = pd.to_datetime(
        timeline_df["Created At"]
    )

    timeline_chart = (
        timeline_df
        .groupby(
            timeline_df["Created At"].dt.date
        )
        .size()
        .reset_index(name="Workflow Count")
    )

    fig_line = px.line(
        timeline_chart,
        x="Created At",
        y="Workflow Count",
        markers=True,
        title="Workflow Activity Over Time"
    )

    fig_line.update_layout(
        paper_bgcolor="#0B0F19",
        plot_bgcolor="#0B0F19",
        font_color="white"
    )

    st.plotly_chart(
        fig_line,
        use_container_width=True
    )


# -----------------------------------
# HISTORY TABLE
# -----------------------------------

st.divider()

st.header("Workflow History")

if history:

    st.dataframe(
        history_df,
        use_container_width=True,
        height=300
    )

else:

    st.info(
        "No workflow history available."
    )