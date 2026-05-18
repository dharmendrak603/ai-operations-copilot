from agents.base_agent import BaseAgent
from tools.tool_registry import TOOLS

class PlannerAgent(BaseAgent):

    def __init__(self):

        system_prompt = """
        You are a Planner Agent.

        Your responsibility is to:
        - understand user requests
        - break tasks into steps
        - decide what kind of analysis is needed
        - create a clear execution plan

        Keep responses structured and concise.
        """

        super().__init__(
            name="Planner Agent",
            system_prompt=system_prompt,
            tools={
                "date_time": TOOLS["date_time"]
            }
        )