import os
import json
import argparse
from dotenv import load_dotenv
import datetime
from langchain_openai import ChatOpenAI

from bargain_langgraph.agents.buyer import BuyerAgent
from bargain_langgraph.agents.seller import SellerAgent
from bargain_langgraph.dynamics.product import Product
from bargain_langgraph.graph.bargaining_graph import build_bargaining_graph
from bargain_langgraph.evaluation.metrics import evaluate_conversation

"""
Main code to parse input arguments and run a single bargaining conversation
Written by: Sunrit Chakraborty
"""

# ------------------------------------------------------------
# Utility loaders
# ------------------------------------------------------------
def load_json(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def load_prompt(path: str) -> str:
    with open(path, "r") as f:
        return f.read()



# ------------------------------------------------------------
# Main
# ------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Run LLM bargaining simulation")
    parser.add_argument("--model", required=False, default='gpt-4.1-mini', help="OpenRouter model name (e.g. gpt-4.1-mini)")
    parser.add_argument("--temp", required=False, default=0.1, help="LLM temperature")
    parser.add_argument("--scenario", required=True, help="Scenario name (without .json)")
    parser.add_argument("--buyer", required=True, help="Buyer profile name")
    parser.add_argument("--seller", required=True, help="Seller profile name")
    parser.add_argument("--max_rounds", required=False, default=10, help="Maximum number of turns for conversation")
    parser.add_argument("--save_to", required=False, default=None, help="Directory to save conversations")

    args = parser.parse_args()

    # ------------------------------------------------------------
    # 1. Environment variables
    # ------------------------------------------------------------
    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")
    if api_key is None:
        raise RuntimeError("OPENROUTER_API_KEY not set")

    # ------------------------------------------------------------
    # 2. Load scenario & profiles
    # ------------------------------------------------------------
    scenario_path = f"bargain_langgraph/scenarios/examples.json"
    profiles_path = "bargain_langgraph/profiles/personas.json"

    scenarios = load_json(scenario_path)
    profiles = load_json(profiles_path)

    if args.buyer not in profiles:
        raise ValueError(f"Buyer profile '{args.buyer}' not found")

    if args.seller not in profiles:
        raise ValueError(f"Seller profile '{args.seller}' not found")

    if args.scenario not in scenarios:
        raise ValueError(f"Scenario '{args.scenario}' not found")

    buyer_profile = profiles[args.buyer]
    seller_profile = profiles[args.seller]
    scenario = scenarios[args.scenario]

    # ------------------------------------------------------------
    # 3. Initialize LLM
    # ------------------------------------------------------------
    llm = ChatOpenAI(
        model=f"openai/{args.model}",
        temperature=args.temp,
        openai_api_key=api_key,
        openai_api_base="https://openrouter.ai/api/v1",
    )

    # ------------------------------------------------------------
    # 4. Load prompts
    # ------------------------------------------------------------
    buyer_prompt = load_prompt("bargain_langgraph/prompts/buyer.txt")
    seller_prompt = load_prompt("bargain_langgraph/prompts/seller.txt")

    buyer_agent = BuyerAgent(llm=llm, prompt_template=buyer_prompt)
    seller_agent = SellerAgent(llm=llm, prompt_template=seller_prompt)

    # ------------------------------------------------------------
    # 5. Construct initial state
    # ------------------------------------------------------------
    product = scenario["product"]

    seller_initial_price = scenario["seller_initial_price"]
    buyer_target_price = scenario["buyer_target_price"]

    initial_state = {
        "round": 0,
        "max_rounds": scenario["max_rounds"],

        "seller_initial_price": seller_initial_price,
        "buyer_target_price": buyer_target_price,

        # Force seller to move first
        "last_seller_price": seller_initial_price,
        "last_buyer_price": buyer_target_price,

        "price_gap": seller_initial_price - buyer_target_price,
        "agreed_price": None,

        "product": product,

        "buyer_value": scenario["buyer_value"],
        "seller_cost": scenario["seller_cost"],

        "buyer_personality": buyer_profile["personality"],
        "buyer_background": buyer_profile["background"],
        "buyer_emotion": buyer_profile["emotion"],

        "seller_personality": seller_profile["personality"],
        "seller_background": seller_profile["background"],
        "seller_emotion": seller_profile["emotion"],

        "history": []
    }

    # ------------------------------------------------------------
    # 6. Build and run graph
    # ------------------------------------------------------------
    graph = build_bargaining_graph(
        buyer_agent=buyer_agent,
        seller_agent=seller_agent,
    )

    final_state = graph.invoke(initial_state)

    # ------------------------------------------------------------
    # 7. Evaluation
    # ------------------------------------------------------------
    metrics = evaluate_conversation(final_state)

    # ------------------------------------------------------------
    # 8. Output
    # ------------------------------------------------------------
    print("\n=== Bargaining finished ===")
    print(f"Scenario: {args.scenario}")
    print(f"Buyer: {args.buyer} | Seller: {args.seller}")
    print(f"Final agreed price: {final_state['agreed_price']}")


    print("\nMetrics:")
    print(f"Rounds taken: {final_state['round']}")
    print(f"Did bargaining end in agreement?: {metrics['success']}")
    print(f"Buyer saving percentage: {metrics['buyer_savings_pct']*100}%")

    print("\nConversation history:")
    for step in final_state["history"]:
        print(step)


    # ----------------------------------------------------------
    # 9. Save (if save_to is provided)
    # ----------------------------------------------------------

    if args.save_to is not None:
        os.makedirs(args.save_to, exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{args.scenario}_{args.buyer}_{args.seller}_{timestamp}.json"
        filepath = os.path.join(args.save_to, filename)

        to_save = {
            "scenario": args.scenario,
            "buyer": args.buyer,
            "seller": args.seller,
            "final_agreed_price": final_state["agreed_price"],
            "rounds_taken": final_state["round"],
            "metrics": metrics,
            "history": final_state["history"],
            "initial_state": initial_state,
        }

        with open(filepath, "w") as f:
            json.dump(to_save, f, indent=2)

        print(f"\nConversation saved to {filepath}")

if __name__ == "__main__":
    main()
