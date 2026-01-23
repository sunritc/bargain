"""
Updates the state of the bargaining process based on last action
Written by: Sunrit Chakraborty
"""

def apply_agent_action(state, role, action, message):
    if not isinstance(action, dict):
        raise TypeError(
            f"[{role}] Expected action dict, got {type(action)}: {action}"
        )

    new_state = state.copy()
    history = list(new_state["history"])

    history.append({
        "role": role,
        "action": action,
        "message": message
    })
    new_state["history"] = history

    action_type = action["type"]

    if action_type == "offer":
        price = float(action["price"])

        if role == "buyer":
            new_state["last_buyer_price"] = price
        else:
            new_state["last_seller_price"] = price

        new_state["price_gap"] = (
            new_state["last_seller_price"]
            - new_state["last_buyer_price"]
        )

    elif action_type == "accept":
        # Agreement happens at the seller's last offer
        new_state["agreed_price"] = new_state["last_seller_price"]

    elif action_type == "breakdown":
        new_state["breakdown"] = True

    # pondering / chit-chat do not change prices
    return new_state