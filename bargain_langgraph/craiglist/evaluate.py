"""
Simple metrics to evaluate the bargaining process
1. Whether the bargaining ended in agreement
2. The number of turns taken
3. Buyer saving percentage = (seller_initial_price - final_agreed_price) / seller_initial_price

"""
import numpy as np

def evaluate_conversation(state: dict) -> dict:
    success = state["agreed_price"] is not None

    if not success:
        return {
            "success": False,
            "turns": state["round"],
            "savings": 0.0,
            "reward": 0.0
        }

    if success:
        turns = state["round"]
        seller_target = state["seller_target"]
        final = state["agreed_price"]
        seller_cost = state["seller_cost"]

        savings = (seller_target - final) / (seller_target - seller_cost)
        reward = savings / (1 + np.log(turns))
    else:
        turns = state["round"]
        savings = 0.0
        reward = 0.0


    return {
        "success": True,
        "turns": turns,
        "savings": savings,
        "reward": reward
    }