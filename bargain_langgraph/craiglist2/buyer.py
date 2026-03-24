from bargain_langgraph.agents.base import Agent
from .emotions import *

def update_buyer_emotion(state):
    type = state["buyer_emotion_type"]

    if type == "dynamic":
        current_emotion = state["buyer_emotion"]
        round = state["round"]
        new_emotion = update_emotion(current_emotion, round, type=type)
    else:
        new_emotion = state["buyer_emotion"]

    return new_emotion


class CraiglistBuyer(Agent):

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
            role = "assistant" if turn["role"] == "buyer" else "user"

            messages.append({
                "role": role,
                "content": turn["message"]
            })

        # ------------------
        # CURRENT STATE (MINIMAL)
        # ------------------
#         messages.append({
#             "role": "user",
#             "content": f"""
# Current situation:
# - Seller's latest offer: {state['current_seller_offer']}
# - Your last offer: {state['current_buyer_offer']}
# - Listing price: {state['listing_price']}
# - Round: {state['round']} of {state['max_rounds']}
#
# Respond with your next message to the seller.
# """
#         })

        return messages

    def act(self, state) -> tuple:

        # ------------------
        # UPDATE EMOTION
        # ------------------
        new_emotion = update_buyer_emotion(state)

        new_state = dict(state.copy())
        new_state["buyer_emotion"] = new_emotion

        # ------------------
        # BUILD CHAT MESSAGES
        # ------------------
        messages = self._build_messages(new_state)

        # ------------------
        # LLM CALL
        # ------------------
        chat_resp = self.llm.invoke(messages)

        message = chat_resp.content.strip()

        if not isinstance(message, str):
            raise TypeError("LLM output is not a string")

        return (
            message,
            new_emotion
        )