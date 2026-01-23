"""
Simple metrics to evaluate the bargaining process
1. Whether the bargaining ended in agreement
2. The number of turns taken
3. Buyer saving percentage = (seller_initial_price - final_agreed_price) / seller_initial_price

"""

def evaluate_conversation(state: dict) -> dict:
    success = state["agreed_price"] is not None

    if not success:
        return {
            "success": False,
            "turns": state["round"],
            "buyer_savings_pct": 0.0,
        }

    initial = state["seller_initial_price"]
    final = state["agreed_price"]

    savings_pct = (initial - final) / initial

    return {
        "success": True,
        "turns": state["round"],
        "buyer_savings_pct": savings_pct,
    }