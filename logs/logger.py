from datetime import datetime


class WorkflowLogger:

    @staticmethod
    def log(message):

        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        log_message = f"[{timestamp}] {message}"

        print(log_message)

        with open("logs/workflow_logs.txt", "a") as file:

            file.write(log_message + "\n")