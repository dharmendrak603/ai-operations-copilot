from agents.base_agent import BaseAgent


class ExecutorAgent(BaseAgent):

    def __init__(self):

        system_prompt = """
        You are an Executor Agent.

        Your responsibility:
        - simulate approved task execution
        - provide execution summaries
        - report operational status clearly

        IMPORTANT:
        Always return your response in this EXACT JSON format:

        {
            "execution_status": "executed" or "failed",
            "execution_summary": "short execution summary"
        }

        Keep responses concise and operational.
        """

        super().__init__(
            name="Executor Agent",
            system_prompt=system_prompt,
            tools={}
        )