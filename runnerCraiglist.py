import os
import json
import argparse
from dotenv import load_dotenv
import datetime
from langchain_openai import ChatOpenAI

from bargain_langgraph.craiglist.state import get_initial_craiglist_state
from bargain_langgraph.craiglist.buyer import CraiglistBuyer
from bargain_langgraph.craiglist.seller import CraiglistSeller
from bargain_langgraph.craiglist.bargaining_graph import build_craiglist_graph
from bargain_langgraph.craiglist.evaluate import evaluate_conversation

# ------------------------------------------------------------
# Utility loaders
# ------------------------------------------------------------

def load_prompt(path: str) -> str:
    with open(path, "r") as f:
        return f.read()


def main():
    parser = argparse.ArgumentParser(description="Run LLM bargaining simulation Cragilist")
    parser.add_argument("--model", required=False, default='gpt-4.1-mini',
                        help="OpenRouter model name (e.g. gpt-4.1-mini)")
    parser.add_argument("--temp", required=False, default=0.1, help="LLM temperature")
    parser.add_argument("--id", required=True, help="Craiglist ID")
    parser.add_argument("--max_rounds", required=False, default=10,
                        help="Maximum number of turns for conversation")
    parser.add_argument("--buyer_emotion", required=False, default=None,
                        help="Buyer emotion (if provided overrides emotion in persona)")
    parser.add_argument("--seller_emotion", required=False, default=None,
                        help="Seller emotion (if provided overrides emotion in persona)")
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
    initial_state = get_initial_craiglist_state(
        id=int(args.id),
        max_rounds=args.max_rounds,
        buyer_emotion=args.buyer_emotion,
        seller_emotion=args.seller_emotion
    )

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
    buyer_prompt = load_prompt("bargain_langgraph/craiglist/prompts/buyer_emo.txt")
    seller_prompt = load_prompt("bargain_langgraph/craiglist/prompts/seller_emo.txt")

    buyer_agent = CraiglistBuyer(llm=llm, prompt=buyer_prompt)
    seller_agent = CraiglistSeller(llm=llm, prompt=seller_prompt)

    # ------------------------------------------------------------
    # 5. Build and run graph
    # ------------------------------------------------------------
    graph = build_craiglist_graph(
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
    print(f"Scenario (ID = {args.id}): {final_state['product_name']}")
    print(f"Model: {args.model} with temperature: {args.temp}")
    print(f"Buyer cost: ${final_state['buyer_cost']} | Seller cost: ${final_state['seller_cost']}")
    print(f"Buyer target: ${final_state['buyer_target']} | Seller target: ${final_state['seller_target']}")
    print(f"Initial offer (by buyer): ${final_state['initial_offer']}")
    print(f"Final agreed price: ${final_state['agreed_price']}")

    print("\nMetrics:")
    print(f"Rounds taken: {final_state['round']}")
    print(f"Did bargaining end in agreement?: {metrics['success']}")
    print(f"Buyer saving percentage: {metrics['savings'] * 100:.3f}%")
    print(f"Buyer reward (evoemo): {metrics['reward']:.3f}%")


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