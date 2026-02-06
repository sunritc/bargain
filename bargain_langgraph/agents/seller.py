import json
from .base import Agent
from bargain_langgraph.dynamics.emotion_discount import *
"""
Describes the seller agent and how this agent acts
Written by: Sunrit Chakraborty
"""
def evolve_seller_emotion_discount(state):
    if state["seller_discount_type"] == "static":
        seller_discount = state["seller_discount"]
    else:
        seller_discount = update_discount(state["seller_discount"],
                                          state["round"],
                                          state["max_rounds"],
                                          state["current_buyer_offer"],
                                          state["seller_cost"],
                                          state["buyer_cost"])

    if state["seller_emotion_type"] == "static":
        seller_emotion = state["seller_emotion"]
    else:
        seller_emotion = update_emotion(seller_discount)

    return seller_emotion, seller_discount

class SellerAgent(Agent):
    def __init__(self, llm, prompt_template: str):
        self.llm = llm
        self.prompt = prompt_template

    def act(self, state) -> tuple[dict, tuple]:
        if state["round"] == 0:
            # First turn: initial offer
            if state["initial_offer"] is None:
                gap = state["buyer_cost"] - state["seller_cost"]
                price = state["buyer_cost"] - 0.05 * gap
                # example: if v_B=150, v_S=100, gap=50, price=150-0.05*50=147.5
            else:
                price = state["initial_offer"]
            name = state["seller_name"]
            message = f"Hi, I am {name}. My first offer is ${price} for the {state['product_name']}. Are you interested?"
            seller_choices = state["seller_emotion"], state["seller_discount"]
            return {"action": "offer", "price": price, "message": message} , seller_choices


        # evolve emotion and/or discount
        seller_choices = evolve_seller_emotion_discount(state)
        seller_emotion, seller_discount = seller_choices

        # bake these into state
        new_state = dict(state.copy())
        new_state["seller_emotion"] = seller_emotion
        new_state["seller_discount"] = seller_discount

        prompt_text = self.prompt.format(**new_state)

        # Build messages
        messages = [
            {"role": "system", "content": "You are a seller agent in a bargaining simulation."},
            {"role": "user", "content": prompt_text}
        ]

        # Call the LLM
        chat_resp = self.llm.invoke(messages)

        # Extract content
        parsed = json.loads(chat_resp.content)

        if not isinstance(parsed, dict):
            raise TypeError("LLM output must be a dict")

        if "action" not in parsed or "message" not in parsed or "price" not in parsed:
            raise ValueError(f"Malformed LLM output: {parsed}")

        return parsed, seller_choices