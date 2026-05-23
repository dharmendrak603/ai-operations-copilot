import logging


# -----------------------------------
# LOGGER CONFIGURATION
# -----------------------------------

logging.basicConfig(

    level=logging.INFO,

    format="%(asctime)s - %(levelname)s - %(message)s"
)


# -----------------------------------
# LOGGER CLASS
# -----------------------------------

class WorkflowLogger:

    @staticmethod
    def log(message):

        logging.info(message)

    @staticmethod
    def info(message):

        logging.info(message)


    @staticmethod
    def error(message):

        logging.error(message)


    @staticmethod
    def warning(message):

        logging.warning(message)


    # -----------------------------------
    # WORKFLOW EVENTS
    # -----------------------------------

    @staticmethod
    def log_workflow_started(workflow_id):

        logging.info(
            f"Workflow Started | ID: {workflow_id}"
        )


    @staticmethod
    def log_workflow_completed(workflow_id):

        logging.info(
            f"Workflow Completed | ID: {workflow_id}"
        )


    @staticmethod
    def log_agent_completed(
        agent_name,
        workflow_id
    ):

        logging.info(
            f"{agent_name} Completed | "
            f"Workflow ID: {workflow_id}"
        )


    @staticmethod
    def log_execution_completed(workflow_id):

        logging.info(
            f"Execution Completed | "
            f"Workflow ID: {workflow_id}"
        )


    @staticmethod
    def log_human_rejected(workflow_id):

        logging.warning(
            f"Human Rejected Workflow | "
            f"Workflow ID: {workflow_id}"
        )