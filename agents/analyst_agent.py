from agents.base_agent import BaseAgent


class AnalystAgent(BaseAgent):

    def __init__(self):

        system_prompt = """
        You are an Analyst Agent.

        Your responsibility is to:
        - analyze requests deeply
        - provide technical insights
        - identify risks or improvements
        - explain findings clearly

        Be analytical and detailed.
        """

        super().__init__(
            name="Analyst Agent",
            system_prompt=system_prompt,
            tools={}
        )