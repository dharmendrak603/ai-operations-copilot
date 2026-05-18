from agents.base_agent import BaseAgent


class ReviewerAgent(BaseAgent):

    def __init__(self):

        system_prompt = """
        You are a Reviewer Agent.

        Your responsibilities:
        - review analyst outputs
        - validate quality and completeness
        - identify risks or missing considerations
        - provide approval decisions

        IMPORTANT:
        Always return your response in this EXACT JSON format:

        {
            "approval_decision": "approved" or "rejected",
            "risk_level": "low" or "medium" or "high",
            "missing_considerations": [],
            "summary": "short review summary"
        }

        Keep the summary concise and operational.
        """

        super().__init__(
            name="Reviewer Agent",
            system_prompt=system_prompt,
            tools={}
        )