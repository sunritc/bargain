from bargain_langgraph.agents.base import Agent
from .emotions import *

def update_seller_emotion(state):
    type = state["seller_emotion_type"]

    if type == "dynamic":
        current_emotion = state["seller_emotion"]
        round = state["round"]
        new_emotion = update_emotion(current_emotion, round, type=type)
    else:
        new_emotion = state["seller_emotion"]

    return new_emotion


class CraiglistSeller(Agent):

    def __init__(self, llm, system_prompt: str):
        self.llm = llm
        self.system_prompt = system_prompt

    def _build_messages(self, state):
        messages = []

        # ------------------
        # SYSTEM PROMPT
        # ------------------
        messages.append({
            "role": "system",
            "content": self.system_prompt.format(**state)
        })

        # ------------------
        # CONVERSATION HISTORY
        # ------------------
        for turn in state["history"]:
            role = "assistant" if turn["role"] == "seller" else "user"

            messages.append({
                "role": role,
                "content": turn["message"]
            })

        # ------------------
        # CURRENT STATE (MINIMAL)
        # ------------------
        seller_offer = state["current_seller_offer"]
        buyer_offer = state["current_buyer_offer"]

#         messages.append({
#             "role": "user",
#             "content": f"""
# Current situation:
# - Your last offer: {seller_offer}
# - Buyer's latest offer: {buyer_offer}
# - Listing price: {state['listing_price']}
# - Round: {state['round']} of {state['max_rounds']}
#
# Respond with your next message to the buyer.
# """
#         })

        return messages

    def act(self, state) -> tuple:

        # ------------------
        # FIRST TURN (ANCHOR)
        # ------------------
        if state["round"] == 0:
            message = (
                f"Hi, I am selling a {state['product_name']} "
                f"for ${state['listing_price']}. Are you interested?"
            )
            return message, state["seller_emotion"]

        # ------------------
        # UPDATE EMOTION
        # ------------------
        new_emotion = update_seller_emotion(state)

        new_state = dict(state.copy())
        new_state["seller_emotion"] = new_emotion

        # ------------------
        # BUILD MESSAGES
        # ------------------
        messages = self._build_messages(new_state)

        # ------------------
        # LLM CALL
        # ------------------
        chat_resp = self.llm.invoke(messages)

        message = chat_resp.content.strip()

        if not isinstance(message, str):
            raise TypeError("LLM output is not a string")

        return message, new_emotion