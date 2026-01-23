import json
from .base import Agent
"""
Describes the buyer agent and how this agent acts
Written by: Sunrit Chakraborty
"""

class BuyerAgent(Agent):
    def __init__(self, llm, prompt_template: str):
        self.llm = llm
        self.prompt = prompt_template

    def act(self, state: dict) -> tuple[dict, str]:
        # Format prompt
        flat_state = dict(state)
        product = state["product"]

        flat_state.update({
            "product_name": product["name"],
            "product_description": product["description"],
            "product_used": product["used"],
            "product_condition": product["condition"],
            "product_new_market_price": product["new_market_price"],
            "product_demand": product["demand"],
        })

        prompt_text = self.prompt.format(**flat_state)

        # Build messages
        messages = [
            {"role": "system", "content": "You are a buyer agent in a bargaining simulation."},
            {"role": "user", "content": prompt_text}
        ]

        # Call the LLM
        chat_resp = self.llm.invoke(messages)
        parsed = json.loads(chat_resp.content)

        if not isinstance(parsed, dict):
            raise TypeError("LLM output must be a dict")

        if "action" not in parsed or "message" not in parsed:
            raise ValueError(f"Malformed LLM output: {parsed}")

        return parsed["action"], parsed["message"]