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

    initial = state["initial_offer"]
    final = state["agreed_price"]

    savings_pct = (initial - final) / initial

    # assuming discount is static
    buyer_discount = state["buyer_discount"]
    seller_discount = state["seller_discount"]
    buyer_cost = state["buyer_cost"]
    seller_cost = state["seller_cost"]
    equilibrium_price = (1 - buyer_discount) * seller_cost / (1 - buyer_discount * seller_discount)
    equilibrium_price += buyer_discount * (1 - seller_discount) * buyer_cost / (1 - buyer_discount * seller_discount)
    above_eq_pct = (final - equilibrium_price) / equilibrium_price

    return {
        "success": True,
        "turns": state["round"],
        "buyer_savings_pct": savings_pct,
        "equilibrium_price": equilibrium_price,
        "above_eq_pct": above_eq_pct
    }