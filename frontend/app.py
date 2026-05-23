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

/* ENTIRE APP BACKGROUND */

.stApp {
    background-color: #0B0F19;
    color: white;
}


/* MAIN PAGE */

.main {
    background-color: #0B0F19;
    color: white;
}


/* GLOBAL TEXT */

html, body, [class*="css"]  {
    font-family: 'Segoe UI', sans-serif;
    color: white;
}


/* REMOVE WHITE CONTAINERS */

[data-testid="stAppViewContainer"] {
    background-color: #0B0F19;
}


[data-testid="stHeader"] {
    background-color: #0B0F19;
}


[data-testid="stToolbar"] {
    right: 2rem;
}


/* SIDEBAR */

section[data-testid="stSidebar"] {

    background-color: #070B12;

    border-right: 1px solid #1E293B;
}


/* MAIN BLOCK */

.block-container {

    padding-top: 1.5rem;

    padding-bottom: 2rem;

    max-width: 95%;
}


/* METRIC CARDS */

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

    transition: 0.3s;
}


[data-testid="metric-container"]:hover {

    border: 1px solid #22C55E;

    transform: translateY(-2px);
}


/* EXPANDERS */

.streamlit-expanderHeader {

    background-color: #111827;

    border-radius: 10px;

    border: 1px solid #1E293B;

    padding: 10px;

    color: white;
}


/* BUTTONS */

.stButton > button {

    width: 100%;

    border-radius: 10px;

    height: 3em;

    background-color: #111827;

    color: white;

    border: 1px solid #334155;

    font-weight: 600;
}


.stButton > button:hover {

    border: 1px solid #22C55E;

    color: #22C55E;
}


/* TEXT AREA */

textarea {

    border-radius: 12px !important;

    border: 1px solid #334155 !important;

    background-color: #111827 !important;

    color: white !important;
}


/* INPUT LABELS */

label, .stTextArea label {

    color: white !important;
}


/* DATAFRAME */

[data-testid="stDataFrame"] {

    border-radius: 12px;

    overflow: hidden;

    border: 1px solid #1E293B;

    background-color: #111827;
}


/* ALERTS */

.stSuccess,
.stInfo,
.stWarning,
.stError {

    border-radius: 12px;
}


/* DIVIDERS */

hr {

    border-color: #1E293B;
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
# MAIN HEADER
# -----------------------------------

st.title("AI Operations Copilot")

st.caption(
    "Multi-Agent AI Orchestration Platform"
)


# -----------------------------------
# USER INPUT
# -----------------------------------

st.subheader("Submit Workflow Request")

user_input = st.text_area(
    "Enter your workflow request:",
    height=150,
    placeholder="Example: Explain AI Agents",
    key="workflow_input"
)


# -----------------------------------
# EXECUTE WORKFLOW
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
                    user_input
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
# DISPLAY WORKFLOW RESULT
# -----------------------------------

if st.session_state.workflow_result:

    workflow_result = (
        st.session_state.workflow_result
    )


    # RESET BUTTON

    col1, col2 = st.columns([8, 2])

    with col2:

        if st.button("Start New Workflow"):

            st.session_state.clear()

            st.rerun()


    st.divider()

    st.header("Workflow Summary")


    # STATUS COLORS

    approval_color = (
        "🟢"
        if workflow_result["approval_status"] == "approved"
        else "🔴"
    )

    execution_color = (
        "🟢"
        if workflow_result["execution_status"] == "executed"
        else "🟡"
    )

    risk_color = (
        "🟢"
        if workflow_result["risk_level"] == "low"
        else "🔴"
    )


    # SUMMARY METRICS

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Workflow Status",
        workflow_result["workflow_status"]
    )

    col2.metric(
        "Approval",
        f"{approval_color} {workflow_result['approval_status']}"
    )

    col3.metric(
        "Execution",
        f"{execution_color} {workflow_result['execution_status']}"
    )

    col4.metric(
        "Risk",
        f"{risk_color} {workflow_result['risk_level']}"
    )


    # DETAILS

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


    with st.expander(
        "🧠 Planner Agent",
        expanded=False
    ):

        st.write(
            workflow_result["planner_response"]
        )


    with st.expander(
        "📊 Analyst Agent",
        expanded=False
    ):

        st.write(
            workflow_result["analyst_response"]
        )


    with st.expander(
        "🛡 Reviewer Agent",
        expanded=False
    ):

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

        if st.button(
            "Submit Human Approval",
            use_container_width=True
        ):

            if human_decision == "Approve":

                workflow_result[
                    "human_approval"
                ] = "approved"

                workflow_result = (
                    workflow_manager.execute_approved_workflow(
                        workflow_result
                    )
                )

                st.session_state.workflow_result = (
                    workflow_result
                )

                st.success(
                    "Workflow Executed Successfully"
                )

                st.rerun()

            else:

                workflow_result[
                    "human_approval"
                ] = "rejected"

                workflow_result = (
                    workflow_manager.execute_approved_workflow(
                        workflow_result
                    )
                )

                st.session_state.workflow_result = (
                    workflow_result
                )

                st.error(
                    "Workflow Execution Rejected"
                )

                st.rerun()


    # -----------------------------------
    # EXECUTION RESULT
    # -----------------------------------

    if workflow_result["executor_response"]:

        st.divider()

        st.header("Execution Result")

        executor_response = (
            workflow_result["executor_response"]
        )

        st.success(
            f"Execution Status: "
            f"{workflow_result['execution_status']}"
        )

        st.info(
            str(executor_response)
        )


# -----------------------------------
# ANALYTICS SECTION
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


    # KPI METRICS

    total_workflows = len(history_df)

    executed_count = len(
        history_df[
            history_df["Execution Status"] == "executed"
        ]
    )

    blocked_count = len(
        history_df[
            history_df["Execution Status"] == "blocked"
        ]
    )

    approval_rate = round(
        (
            len(
                history_df[
                    history_df["Approval Status"] == "approved"
                ]
            )
            / total_workflows
        ) * 100,
        1
    )


    # KPI CARDS

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Workflows",
        total_workflows
    )

    col2.metric(
        "Executed",
        executed_count
    )

    col3.metric(
        "Blocked",
        blocked_count
    )

    col4.metric(
        "Approval Rate",
        f"{approval_rate}%"
    )


    # CHARTS

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


    # TIMELINE CHART

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