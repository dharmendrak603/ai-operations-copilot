import sqlite3
import os


class DatabaseManager:

    def __init__(self):

        BASE_DIR = os.path.dirname(
            os.path.abspath(__file__)
        )

        db_path = os.path.join(
            BASE_DIR,
            "workflow.db"
        )

        self.connection = sqlite3.connect(db_path)

        self.cursor = self.connection.cursor()

        self.create_workflow_table()

    def create_workflow_table(self):

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS workflows (

            workflow_id TEXT PRIMARY KEY,

            user_input TEXT,

            workflow_status TEXT,

            approval_status TEXT,

            human_approval TEXT,

            execution_status TEXT,

            risk_level TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        self.connection.commit()

    def save_workflow(self, workflow_state):

        self.cursor.execute("""
        INSERT INTO workflows (

            workflow_id,
            user_input,
            workflow_status,
            approval_status,
            human_approval,
            execution_status,
            risk_level

        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (

            str(workflow_state["workflow_id"]),
            workflow_state["user_input"],
            workflow_state["workflow_status"],
            workflow_state["approval_status"],
            workflow_state["human_approval"],
            workflow_state["execution_status"],
            workflow_state["risk_level"]

        ))

        self.connection.commit()

    def get_workflow_history(self):

        self.cursor.execute("""
        SELECT
            workflow_id,
            approval_status,
            human_approval,
            execution_status,
            risk_level,
            created_at
        FROM workflows
        ORDER BY created_at DESC
        """)

        rows = self.cursor.fetchall()

        return rows