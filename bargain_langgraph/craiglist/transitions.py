"""
Transitions for cragilist bargaining
"""

def craiglist_apply_buyer_action(state, action, emotion):
    if not isinstance(action, dict):
        raise TypeError("Action must be a dict")
    new_state = state.copy()

    new_state["buyer_emotion"] = emotion
    new_state["last_message"] = action["message"]

    # update conversation history
    history = list(new_state["history"])

    if not new_state["agreement_reached"]:
        history.append({
            "role": "buyer",
            "action": action["action"],
            "price": action["price"],
            "message": action["message"],
            "emotion": emotion
        })
        new_state["history"] = history

    if state["round"] == 0:
        new_state["initial_offer"] = float(action["price"])
        new_state["price_gap"] = abs(new_state["initial_offer"] - new_state["listing_price"])

    if action["action"] == "offer":
        price = float(action["price"])
        new_state["last_buyer_offer"] = state["current_buyer_offer"]
        new_state["current_buyer_offer"] = price
        new_state["current_offer_by"] = "buyer"
        new_state["price_gap"] = abs(new_state["current_buyer_offer"] - new_state["current_seller_offer"])

    elif action["action"] == "accept":
        if not new_state.get("agreement_reached", False):
            new_state["agreement_reached"] = True
            new_state["agreed_price"] = new_state["current_seller_offer"]

    elif action["action"] == "walk away":
        new_state["breakdown"] = True

    return new_state

def craiglist_apply_seller_action(state, action, emotion):
    if not isinstance(action, dict):
        raise TypeError("Action must be a dict")

    new_state = state.copy()
    new_state["last_message"] = action["message"]
    new_state["seller_emotion"] = emotion

    history = list(new_state["history"])
    if not new_state["agreement_reached"]:
        history.append({
            "role": "seller",
            "action": action["action"],
            "price": action["price"],
            "message": action["message"],
            "emotion": emotion
        })
        new_state["history"] = history

    if action["action"] == "offer":
        price = float(action["price"])
        new_state["last_seller_offer"] = state["current_seller_offer"]
        new_state["current_seller_offer"] = price
        new_state["current_offer_by"] = "seller"
        if new_state["round"] > 0:
            new_state["price_gap"] = abs(new_state["current_seller_offer"] - new_state["current_buyer_offer"])

    elif action["action"] == "accept":
        if not new_state.get("agreement_reached", False):
            new_state["agreement_reached"] = True
            new_state["agreed_price"] = new_state["current_buyer_offer"]

    elif action["action"] == "walk away":
        new_state["breakdown"] = True

    return new_state