from langgraph.graph import StateGraph
from bargain_langgraph.craiglist2.transitions import (
    craiglist_apply_seller_action,
    craiglist_apply_buyer_action
)
from bargain_langgraph.craiglist2.state import CraiglistState


def build_craiglist_graph(
    buyer_agent,
    seller_agent,
    checker
):

    graph = StateGraph(CraiglistState)

    # =========================
    # SELLER NODE (LLM)
    # =========================
    def seller_node(state):
        message, emotion = seller_agent.act(state)

        new_state = state.copy()
        new_state["pending_message"] = message
        new_state["seller_emotion"] = emotion

        return new_state

    # =========================
    # SELLER CHECK NODE
    # =========================
    def seller_check_node(state):
        message = state.get("pending_message")
        if message is None:
            # no message yet → just return state
            return state

        parsed = checker.parse(
            state,
            message,
            role="seller"
        )

        action = {
            "action": parsed["action"],
            "price": parsed["price"],
            "message": message
        }

        return craiglist_apply_seller_action(
            state,
            action,
            state.get("seller_emotion", "neutral")
        )

    # =========================
    # BUYER NODE (LLM)
    # =========================
    def buyer_node(state):
        message, emotion = buyer_agent.act(state)

        new_state = state.copy()
        new_state["pending_message"] = message
        new_state["buyer_emotion"] = emotion

        return new_state

    # =========================
    # BUYER CHECK NODE
    # =========================
    def buyer_check_node(state):
        message = state.get("pending_message")
        if message is None:
            return state

        parsed = checker.parse(
            state,
            message,
            role="buyer"
        )

        action = {
            "action": parsed["action"],
            "price": parsed["price"],
            "message": message
        }

        return craiglist_apply_buyer_action(
            state,
            action,
            state.get("buyer_emotion", "neutral")
        )

    # =========================
    # ROUND INCREMENT
    # =========================
    def increment_round(state):
        new_state = state.copy()
        new_state["round"] += 1
        return new_state

    # =========================
    # TERMINATION LOGIC
    # =========================
    def should_continue(state):

        if state.get("agreement_reached"):
            return "end"

        if state.get("breakdown"):
            return "end"

        if state["round"] >= state["max_rounds"]:
            return "end"

        # sanity constraints
        if state["round"] >= 1:
            if (
                state.get("current_seller_offer") is not None and
                state["current_seller_offer"] < state["seller_cost"]
            ):
                return "end"

            if (
                state.get("current_buyer_offer") is not None and
                state["current_buyer_offer"] > state["buyer_cost"]
            ):
                return "end"

        return "continue"

    # =========================
    # GRAPH STRUCTURE
    # =========================
    graph.add_node("seller", seller_node)
    graph.add_node("seller_check", seller_check_node)

    graph.add_node("buyer", buyer_node)
    graph.add_node("buyer_check", buyer_check_node)

    graph.add_node("round", increment_round)

    # entry point
    graph.set_entry_point("seller")

    # flow
    graph.add_edge("seller", "seller_check")
    graph.add_edge("seller_check", "buyer")

    graph.add_edge("buyer", "buyer_check")
    graph.add_edge("buyer_check", "round")

    # loop / terminate
    graph.add_conditional_edges(
        "round",
        should_continue,
        {
            "continue": "seller",
            "end": "__end__"
        }
    )

    return graph.compile()