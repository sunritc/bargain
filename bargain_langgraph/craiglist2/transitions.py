"""
Transitions for craigslist bargaining (checker-based pipeline)
"""


def _safe_price(price):
    if price is None:
        return None
    try:
        return float(price)
    except Exception:
        return None


# =========================
# BUYER TRANSITION
# =========================
def craiglist_apply_buyer_action(state, action, emotion):

    if not isinstance(action, dict):
        raise TypeError("Action must be a dict")

    new_state = state.copy()

    act = action.get("action")
    price = _safe_price(action.get("price"))
    message = action.get("message")

    # ------------------
    # BASIC UPDATES
    # ------------------
    new_state["buyer_emotion"] = emotion
    new_state["last_message"] = message

    # ------------------
    # HISTORY
    # ------------------
    if not new_state["agreement_reached"]:
        history = list(new_state["history"])
        history.append({
            "role": "buyer",
            "action": act,
            "price": price,
            "message": message,
            "emotion": emotion
        })
        new_state["history"] = history

    # ------------------
    # INITIAL OFFER
    # ------------------
    if state["round"] == 0 and act == "offer" and price is not None:
        new_state["initial_offer"] = price
        if new_state["listing_price"] is not None:
            new_state["price_gap"] = abs(price - new_state["listing_price"])

    # ------------------
    # ACTION LOGIC
    # ------------------
    if act == "offer" and price is not None:

        new_state["last_buyer_offer"] = state["current_buyer_offer"]
        new_state["current_buyer_offer"] = price
        new_state["current_offer_by"] = "buyer"

        if state["current_seller_offer"] is not None:
            new_state["price_gap"] = abs(price - state["current_seller_offer"])


    elif act == "accept":
        if not new_state.get("agreement_reached", False):
            if state["current_seller_offer"] is not None:
                new_state["agreement_reached"] = True
                new_state["agreed_price"] = state["current_seller_offer"]
            else:
                # invalid accept → ignore (or treat as stay)
                new_state.setdefault("debug_logs", []).append(
                    "Invalid accept: no available offer"
                )

    elif act == "walk-away":
        new_state["breakdown"] = True

    # "stay" → no structural change

    return new_state


# =========================
# SELLER TRANSITION
# =========================
def craiglist_apply_seller_action(state, action, emotion):

    if not isinstance(action, dict):
        raise TypeError("Action must be a dict")

    new_state = state.copy()

    act = action.get("action")
    price = _safe_price(action.get("price"))
    message = action.get("message")

    # ------------------
    # BASIC UPDATES
    # ------------------
    new_state["seller_emotion"] = emotion
    new_state["last_message"] = message

    # ------------------
    # HISTORY
    # ------------------
    if not new_state["agreement_reached"]:
        history = list(new_state["history"])
        history.append({
            "role": "seller",
            "action": act,
            "price": price,
            "message": message,
            "emotion": emotion
        })
        new_state["history"] = history

    # ------------------
    # ACTION LOGIC
    # ------------------
    if act == "offer" and price is not None:

        new_state["last_seller_offer"] = state["current_seller_offer"]
        new_state["current_seller_offer"] = price
        new_state["current_offer_by"] = "seller"

        if state["current_buyer_offer"] is not None:
            new_state["price_gap"] = abs(price - state["current_buyer_offer"])


    elif act == "accept":
        if not new_state.get("agreement_reached", False):
            if state["current_buyer_offer"] is not None:
                new_state["agreement_reached"] = True
                new_state["agreed_price"] = state["current_buyer_offer"]
            else:
                # invalid accept → ignore (or treat as stay)
                new_state.setdefault("debug_logs", []).append(
                    "Invalid accept: no available offer"
                )

    elif act == "walk-away":
        new_state["breakdown"] = True

    # "stay" → no structural change

    return new_state