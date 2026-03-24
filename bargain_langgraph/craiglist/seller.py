import json
from bargain_langgraph.agents.base import Agent
from .emotions import *

def update_seller_emotion(state):

    # if static, then return current emotion - else see emotions.py
    type = state["seller_emotion_type"]

    if type == "dynamic":
        # static behavior for now
        current_emotion = state["seller_emotion"]
        round = state["round"]
        new_emotion = update_emotion(current_emotion, round, type=type)
    else:
        new_emotion = state["seller_emotion"]
    return new_emotion

class CraiglistSeller(Agent):

    def __init__(self, llm, prompt: str):
        self.llm = llm
        self.prompt = prompt

    def act(self, state) -> tuple:

        if state["round"] == 0:
            message = f"Hi, I am selling a {state['product_name']} for ${state['listing_price']}. Are you interested?"
            return ({
                "action": "offer",
                "price": state["listing_price"],
                "message": message
            }, state["seller_emotion"])


        new_emotion = update_seller_emotion(state)
        new_state = dict(state.copy())
        new_state["seller_emotion"] = new_emotion

        prompt_text = self.prompt.format(**new_state)

        messages = [
            {"role": "system", "content": "You are a seller agent in a bargaining scenario."},
            {"role": "user", "content": prompt_text},
        ]

        chat_resp = self.llm.invoke(messages)
        parsed = json.loads(chat_resp.content)

        if not isinstance(parsed, dict):
            raise TypeError("LLM output is not a dict")

        if "action" not in parsed or "message" not in parsed or "price" not in parsed:
            raise ValueError("Malformed LLM output")

        return (
            parsed,
            new_emotion
        )