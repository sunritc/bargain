"""
Updates the state of the bargaining process based on last action
Written by: Sunrit Chakraborty
"""
def apply_buyer_action(state, action, inference, buyer_choices):
    if not isinstance(action, dict):
        raise TypeError(
            f"[Buyer] Expected action dict, got {type(action)}: {action}"
        )
    new_state = state.copy()
    history = list(new_state["history"])

    buyer_emotion, buyer_discount = buyer_choices
    new_state["buyer_emotion"] = buyer_emotion
    new_state["buyer_discount"] = buyer_discount

    seller_cost_hat, seller_emotion_hat, seller_discount_hat = inference
    new_state["infer_seller_cost"] = seller_cost_hat
    new_state["infer_seller_emotion"] = seller_emotion_hat
    new_state["infer_seller_discount"] = seller_discount_hat
    new_state["last_message"] = action["message"]

    history.append({
        "role": "buyer",
        "action": action["action"],
        "price": action["price"],
        "message": action["message"],
        "emotion": buyer_emotion,
        "discount": buyer_discount
    })
    new_state["history"] = history

    action_type = action["action"]

    if action_type == "offer":
        price = float(action["price"])
        new_state["last_buyer_offer"] = state["current_buyer_offer"]
        new_state["current_buyer_offer"] = price
        new_state["current_offer_by"] = "buyer"

    elif action_type == "accept":
        if not new_state.get("agreement_reached", False):
            # Agreement happens at the seller's last offer
            new_state["agreed_price"] = new_state["current_seller_offer"]
            new_state["agreement_reached"] = True

    elif action_type == "breakdown":
        new_state["breakdown"] = True

    # pondering / chit-chat do not change prices
    return new_state


def apply_seller_action(state, action, seller_choices):
    if not isinstance(action, dict):
        raise TypeError(
            f"[Seller] Expected action dict, got {type(action)}: {action}"
        )

    new_state = state.copy()
    new_state["last_message"] = action["message"]

    if state["round"] == 0:
        history = list(new_state["history"])
        history.append({
            "role": "seller",
            "action": action["action"],
            "price": action["price"],
            "message": action["message"],
            "emotion": state["seller_emotion"],
            "discount": state["seller_discount"]
        })
        new_state["history"] = [history]
        new_state["initial_offer"] = float(action["price"])
        new_state["current_seller_offer"] = float(action["price"])
        new_state["current_offer_by"] = "seller"
        new_state["seller_emotion"] = state["seller_emotion"]
        new_state["seller_discount"] = state["seller_discount"]

        return new_state
    else:
        seller_emotion, seller_discount = seller_choices
        history = list(new_state["history"])
        history.append({
            "role": "seller",
            "action": action["action"],
            "price": action["price"],
            "message": action["message"],
            "emotion": seller_emotion,
            "discount": seller_discount
        })
        new_state["history"] = history
        new_state["seller_emotion"] = state["seller_emotion"]
        new_state["seller_discount"] = state["seller_discount"]
        action_type = action["action"]

        if action_type == "offer":
            price = float(action["price"])
            new_state["last_seller_offer"] = state["current_seller_offer"]
            new_state["current_seller_offer"] = price
            new_state["current_offer_by"] = "seller"

        elif action_type == "accept":
            if not new_state.get("agreement_reached", False):
                # Agreement happens at the seller's last offer
                new_state["agreed_price"] = new_state["current_buyer_offer"]
                new_state["agreement_reached"] = True

        elif action_type == "breakdown":
            new_state["breakdown"] = True

        # pondering / chit-chat do not change prices
        return new_state


# def apply_agent_action(state, role, action, message):
#     if not isinstance(action, dict):
#         raise TypeError(
#             f"[{role}] Expected action dict, got {type(action)}: {action}"
#         )
#
#     new_state = state.copy()
#     history = list(new_state["history"])
#
#     history.append({
#         "role": role,
#         "action": action,
#         "message": message
#     })
#     new_state["history"] = history
#
#     action_type = action["type"]
#
#     if action_type == "offer":
#         price = float(action["price"])
#
#         if role == "buyer":
#             new_state["last_buyer_price"] = price
#         else:
#             new_state["last_seller_price"] = price
#
#         new_state["price_gap"] = (
#             new_state["last_seller_price"]
#             - new_state["last_buyer_price"]
#         )
#
#     elif action_type == "accept":
#         # Agreement happens at the seller's last offer
#         new_state["agreed_price"] = new_state["last_seller_price"]
#
#     elif action_type == "breakdown":
#         new_state["breakdown"] = True
#
#     # pondering / chit-chat do not change prices
#     return new_state