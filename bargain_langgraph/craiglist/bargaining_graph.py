from langgraph.graph import StateGraph
from bargain_langgraph.craiglist.transitions import craiglist_apply_seller_action, craiglist_apply_buyer_action
from bargain_langgraph.craiglist.state import CraiglistState

def build_craiglist_graph(
        buyer_agent,
        seller_agent
):
    graph = StateGraph(CraiglistState)

    # ------------------
    # SELLER TURN
    # ------------------
    def seller_node(state):
        action, emotion = seller_agent.act(state)
        return craiglist_apply_seller_action(state, action, emotion)

    # ------------------
    # BUYER TURN
    # ------------------
    def buyer_node(state):
        action, emotion = buyer_agent.act(state)
        return craiglist_apply_buyer_action(state, action, emotion)


    def increment_round(state):
        new_state = state.copy()
        new_state["round"] += 1
        return new_state

    def should_continue(state):
        if state.get("agreement_reached"):
            return "end"

        if state.get("breakdown"):
            print("Breakdown")
            return "end"

        if state["round"] >= state["max_rounds"]:
            return "end"

        if state["round"] >= 1:
            if (state["current_seller_offer"] < state["seller_cost"]) or (state["current_buyer_offer"] > state["buyer_cost"]):
                return "end" # this can be tracked - ended but agreement is False, breakdown is False

        return "continue"

    graph.add_node("buyer", buyer_node)
    graph.add_node("seller", seller_node)
    graph.add_node("round", increment_round)

    graph.set_entry_point("seller") # buyer starts conversation

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
