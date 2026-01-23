from langgraph.graph import StateGraph
from bargain_langgraph.dynamics.transitions import apply_agent_action

"""
Build the state graph in langchain, alternating between seller and buyer nodes
Written by: Sunrit Chakraborty
"""

def build_bargaining_graph(buyer_agent, seller_agent):
    graph = StateGraph(dict)

    # -------------------------
    # Seller turn
    # -------------------------
    def seller_node(state):
        action, message = seller_agent.act(state)
        return apply_agent_action(state, "seller", action, message)

    # -------------------------
    # Buyer turn
    # -------------------------
    def buyer_node(state):
        action, message = buyer_agent.act(state)
        return apply_agent_action(state, "buyer", action, message)

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
        if state.get("agreed_price") is not None:
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

    graph.set_entry_point("seller")

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