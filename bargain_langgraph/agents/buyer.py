import json
from .base import Agent
"""
Describes the buyer agent and how this agent acts
Written by: Sunrit Chakraborty

functions buyer_inference and buyer_emotion_discount ---> naive
To do: update these, as required
"""

def buyer_inference(state):
    # buyer's inference on seller cost, emotion and discount
    # currently, full-information behavior
    if state["buyer_inference"]:
        return (state["seller_cost"], state["seller_emotion"], state["seller_discount"])
    else:
        return (None, None, None)

def buyer_emotion_discount_choice(state,
                                  inference):
    # Buyer's adaptive decision to change emotion and/or discount
    # inference is output of buyer_inference
    # currently, static behavior only implemented

    buyer_emotion_type = state["buyer_emotion_type"]
    buyer_discount_type = state["buyer_discount_type"]

    return (state["buyer_emotion"], state["buyer_discount"])

class BuyerAgent(Agent):
    def __init__(self, llm, prompt_template: str):
        self.llm = llm
        self.prompt = prompt_template

    def act(self, state) -> tuple[dict, tuple, tuple]:

        # if buyer_inference is True: make inference on seller info
        inference = buyer_inference(state)
        seller_cost_hat, seller_emotion_hat, seller_discount_hat = inference

        # make choices on emotion and discount for buyer
        buyer_choices = buyer_emotion_discount_choice(state,
                                                      inference)
        buyer_emotion, buyer_discount = buyer_choices

        # bake these into state
        new_state = dict(state.copy())
        new_state["infer_seller_cost"] = seller_cost_hat
        new_state["infer_seller_emotion"] = seller_emotion_hat
        new_state["infer_seller_discount"] = seller_discount_hat
        new_state["buyer_emotion"] = buyer_emotion
        new_state["buyer_discount"] = buyer_discount

        prompt_text = self.prompt.format(**new_state)

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

        if "action" not in parsed or "message" not in parsed or "price" not in parsed:
            raise ValueError(f"Malformed LLM output: {parsed}")

        return (parsed,
                inference,
                buyer_choices)