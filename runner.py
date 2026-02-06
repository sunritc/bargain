import os
import json
import argparse
from dotenv import load_dotenv
import datetime
from langchain_openai import ChatOpenAI

from bargain_langgraph.agents.buyer import BuyerAgent
from bargain_langgraph.agents.seller import SellerAgent
from bargain_langgraph.dynamics.state import get_initial_state
from bargain_langgraph.graph.bargaining_graph import build_bargaining_graph
from bargain_langgraph.evaluation.metrics import evaluate_conversation

"""
Main code to parse input arguments and run a single bargaining conversation
Written by: Sunrit Chakraborty
"""

# ------------------------------------------------------------
# Utility loaders
# ------------------------------------------------------------

def load_prompt(path: str) -> str:
    with open(path, "r") as f:
        return f.read()



# ------------------------------------------------------------
# Main
# ------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Run LLM bargaining simulation")
    parser.add_argument("--model", required=False, default='gpt-4.1-mini',
                        help="OpenRouter model name (e.g. gpt-4.1-mini)")
    parser.add_argument("--temp", required=False, default=0.1, help="LLM temperature")
    parser.add_argument("--product_name", required=True, help="Product name (e.g. 'Laptop001')")
    parser.add_argument("--buyer_name", required=True, help="Buyer profile name (e.g. 'Ravi')")
    parser.add_argument("--seller_name", required=True, help="Seller profile name (e.g. 'Ravi')")
    parser.add_argument("--max_rounds", required=False, default=10,
                        help="Maximum number of turns for conversation")

    parser.add_argument("--buyer_emotion", required=False, default=None,
                        help="Buyer emotion (if provided overrides emotion in persona)")
    parser.add_argument("--seller_emotion", required=False, default=None,
                        help="Seller emotion (if provided overrides emotion in persona)")

    parser.add_argument("--buyer_discount", required=False, default=None,
                        help="Buyer discount (if provided overrides discount in persona)")
    parser.add_argument("--seller_discount", required=False, default=None,
                        help="Seller discount (if provided overrides discount in persona)")

    parser.add_argument("--seller_emotion_type", required=False, default="static",
                        help="If seller emotion type is static or dynamic")
    parser.add_argument("--seller_discount_type", required=False, default="static",
                        help="If seller discount type is static or dynamic")

    parser.add_argument("--buyer_emotion_type", required=False, default="static",
                        help="If buyer emotion type is static or dynamic")
    parser.add_argument("--buyer_discount_type", required=False, default="static",
                        help="If buyer discount type is static or dynamic")

    parser.add_argument("--buyer_inference", required=False, default=False,
                        help="If buyer makes inference on seller private info (currently True defaults to full information setting")

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
    # 2. Construct initial state
    # ------------------------------------------------------------

    if args.seller_discount_type == "static" and args.seller_emotion_type == "static":
        seller_static = ["emotion", "discount"]
    elif args.seller_discount_type == "dynamic" and args.seller_emotion_type == "static":
        seller_static = ["emotion"]
    elif args.seller_discount_type == "static" and args.seller_emotion_type == "dynamic":
        seller_static = ["discount"]
    else:
        seller_static = None

    if args.buyer_discount_type == "static" and args.buyer_emotion_type == "static":
        buyer_static = ["emotion", "discount"]
    elif args.buyer_discount_type == "dynamic" and args.buyer_emotion_type == "static":
        buyer_static = ["emotion"]
    elif args.buyer_discount_type == "static" and args.buyer_emotion_type == "dynamic":
        buyer_static = ["discount"]
    else:
        buyer_static = None

    initial_state = get_initial_state(args.product_name,
                                      args.buyer_name,
                                      args.seller_name,
                                      args.max_rounds,
                                      seller_static,
                                      buyer_static,
                                      args.buyer_inference)

    # if emotions/discounts are provided, override these in the state
    if args.seller_emotion is not None:
        initial_state["seller_emotion"] = args.seller_emotion
    if args.buyer_emotion is not None:
        initial_state["buyer_emotion"] = args.buyer_emotion
    if args.seller_discount is not None:
        initial_state["seller_discount"] = args.seller_discount
    if args.buyer_discount is not None:
        initial_state["buyer_discount"] = args.buyer_discount

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
    # 5. Build and run graph
    # ------------------------------------------------------------
    graph = build_bargaining_graph(
        buyer_agent=buyer_agent,
        seller_agent=seller_agent,
    )

    final_state = graph.invoke(initial_state)

    # ------------------------------------------------------------
    # 6. Evaluation
    # ------------------------------------------------------------
    metrics = evaluate_conversation(final_state)

    # ------------------------------------------------------------
    # 7. Output
    # ------------------------------------------------------------
    print("\n=== Bargaining finished ===")
    print(f"Scenario: {args.product_name}")
    print(f"Model: {args.model} with temperature: {args.temp}")
    print(f"Buyer: {args.buyer_name} | Seller: {args.seller_name}")
    print(f"Buyer cost: ${final_state['buyer_cost']} | Seller cost: ${final_state['seller_cost']}")
    print(f"Initial offer (by seller): ${final_state['initial_offer']}")
    print(f"Final agreed price: ${final_state['agreed_price']}")


    print("\nMetrics:")
    print(f"Rounds taken: {final_state['round']}")
    print(f"Did bargaining end in agreement?: {metrics['success']}")
    print(f"Buyer saving percentage: {metrics['buyer_savings_pct']*100:.3f}%")
    print(f"Assuming discounts are static, Rubinstein equilibrium price: ${metrics['equilibrium_price']:.3f}")
    print(f"Percentage settled above equilibrium: {metrics['above_eq_pct']*100:.3f}% (higher is worse)")

    print("\nConversation history:")
    for step in final_state["history"]:
        print(f"{step} \n")


    # ----------------------------------------------------------
    # 8. Save (if save_to is provided)
    # ----------------------------------------------------------

    if args.save_to is not None:
        os.makedirs(args.save_to, exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        if args.buyer_emotion is not None and args.seller_emotion is not None:
            filename = f"{args.product_name}_{args.buyer_name}_({args.buyer_emotion})_{args.seller_name}_({args.seller_emotion})_{timestamp}.json"
        elif args.buyer_emotion is not None:
            filename = f"{args.product_name}_{args.buyer_name}_({args.buyer_emotion})_{args.seller_name}_{timestamp}.json"
        elif args.seller_emotion is not None:
            filename = f"{args.product_name}_{args.buyer_name}_{args.seller_name}_({args.seller_emotion})_{timestamp}.json"
        else:
            filename = f"{args.product_name}_{args.buyer_name}_{args.seller_name}_{timestamp}.json"

        filepath = os.path.join(args.save_to, filename)

        to_save = {
            "scenario": args.product_name,
            "buyer": args.buyer_name,
            "seller": args.seller_name,
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
