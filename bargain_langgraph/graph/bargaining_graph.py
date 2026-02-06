from langgraph.graph import StateGraph
from bargain_langgraph.dynamics.transitions import apply_buyer_action, apply_seller_action
from bargain_langgraph.dynamics.state import State
"""
Build the state graph in langchain, alternating between seller and buyer nodes
Written by: Sunrit Chakraborty
"""

def build_bargaining_graph(buyer_agent, seller_agent):
    graph = StateGraph(State)

    # -------------------------
    # Seller turn
    # -------------------------
    def seller_node(state):
        action, seller_choices = seller_agent.act(state)
        return apply_seller_action(state, action, seller_choices)

    # -------------------------
    # Buyer turn
    # -------------------------
    def buyer_node(state):
        action, inference, buyer_choices = buyer_agent.act(state)
        return apply_buyer_action(state, action, inference, buyer_choices)

    # -------------------------
    # Round increment
    # -------------------------
    def increment_round(state):
        new_state = state.copy()
        new_state["round"] += 1
        return new_state

    # -------------------------
    # Stop conditions
    # -------------------------
    def should_continue(state):
        if state.get("agreement_reached"):
            return "end"

        if state.get("breakdown", False):
            return "end"

        if state["round"] >= state["max_rounds"]:
            return "end"

        return "continue"

    # -------------------------
    # Graph structure
    # -------------------------
    graph.add_node("seller", seller_node)
    graph.add_node("buyer", buyer_node)
    graph.add_node("round", increment_round)

    graph.set_entry_point("seller") # seller acts first

    graph.add_edge("seller", "buyer")
    graph.add_edge("buyer", "round")

    graph.add_conditional_edges(
        "round",
        should_continue,
        {
            "continue": "seller",
            "end": "__end__"
        }
    )

    return graph.compile()