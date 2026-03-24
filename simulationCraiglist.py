import os
import json
import csv
import argparse
from itertools import product

import numpy as np
from tqdm import tqdm
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from bargain_langgraph.craiglist.state import get_initial_craiglist_state
from bargain_langgraph.craiglist.buyer import CraiglistBuyer
from bargain_langgraph.craiglist.seller import CraiglistSeller
from bargain_langgraph.craiglist.bargaining_graph import build_craiglist_graph
from bargain_langgraph.craiglist.evaluate import evaluate_conversation


# ------------------------------------------------------------
# Utility functions
# ------------------------------------------------------------

def load_prompt(path: str) -> str:
    with open(path, "r") as f:
        return f.read()


def json_converter(obj):
    """Convert numpy types to native Python types for JSON."""
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Type {type(obj)} not serializable")


# ------------------------------------------------------------
# Main simulation
# ------------------------------------------------------------

def main():

    parser = argparse.ArgumentParser(description="Run Craigslist bargaining simulations")

    parser.add_argument("--model", default="gpt-4.1-mini")
    parser.add_argument("--temp", type=float, default=0.1)
    parser.add_argument("--n_scenarios", type=int, required=True)
    parser.add_argument("--save_dir", default="simulation_results_craiglist")

    args = parser.parse_args()

    os.makedirs(args.save_dir, exist_ok=True)

    # ------------------------------------------------------------
    # Emotion list
    # ------------------------------------------------------------

    emotions = [
        "anger",
        "disgust",
        "fear",
        "happy",
        "sad",
        "surprise",
        "neutral"
    ]

    # ------------------------------------------------------------
    # Load environment
    # ------------------------------------------------------------

    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")

    if api_key is None:
        raise RuntimeError("OPENROUTER_API_KEY not set")

    # ------------------------------------------------------------
    # Initialize LLM
    # ------------------------------------------------------------

    llm = ChatOpenAI(
        model=f"openai/{args.model}",
        temperature=args.temp,
        openai_api_key=api_key,
        openai_api_base="https://openrouter.ai/api/v1",
    )

    # ------------------------------------------------------------
    # Load prompts
    # ------------------------------------------------------------

    buyer_prompt = load_prompt("bargain_langgraph/craiglist/prompts/buyer_emo.txt")
    seller_prompt = load_prompt("bargain_langgraph/craiglist/prompts/seller_emo.txt")

    buyer_agent = CraiglistBuyer(llm=llm, prompt=buyer_prompt)
    seller_agent = CraiglistSeller(llm=llm, prompt=seller_prompt)

    graph = build_craiglist_graph(
        buyer_agent=buyer_agent,
        seller_agent=seller_agent,
    )

    # ------------------------------------------------------------
    # Output files
    # ------------------------------------------------------------

    csv_path = os.path.join(args.save_dir, "results.csv")
    jsonl_path = os.path.join(args.save_dir, "histories.jsonl")

    fieldnames = [
        "id",
        "product_name",
        "buyer_cost",
        "seller_cost",
        "buyer_target",
        "seller_target",
        "buyer_emotion",
        "seller_emotion",
        "success",
        "turns",
        "savings",
        "reward",
    ]

    # Write CSV header if file doesn't exist
    if not os.path.exists(csv_path):
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

    # ------------------------------------------------------------
    # Total runs
    # ------------------------------------------------------------

    total_runs = args.n_scenarios * len(emotions) * len(emotions)

    pbar = tqdm(
        total=total_runs,
        desc="Negotiation simulations",
        ncols=100
    )

    # ------------------------------------------------------------
    # Simulation loops
    # ------------------------------------------------------------

    for scenario_id in range(args.n_scenarios):

        for buyer_emotion, seller_emotion in product(emotions, emotions):

            # ------------------------------------------
            # Construct initial state
            # ------------------------------------------

            initial_state = get_initial_craiglist_state(
                id=scenario_id,
                buyer_emotion=buyer_emotion,
                seller_emotion=seller_emotion,
            )

            # ------------------------------------------
            # Run negotiation graph
            # ------------------------------------------

            final_state = graph.invoke(initial_state)

            # ------------------------------------------
            # Evaluate conversation
            # ------------------------------------------

            metrics = evaluate_conversation(final_state)

            # ------------------------------------------
            # Save history (JSONL)
            # ------------------------------------------

            history_entry = {
                "id": scenario_id,
                "product_name": final_state["product_name"],
                "buyer_emotion": buyer_emotion,
                "seller_emotion": seller_emotion,
                "initial_state": initial_state,
                "final_state": final_state,
                "metrics": metrics,
            }

            with open(jsonl_path, "a") as f:
                f.write(json.dumps(history_entry, default=json_converter) + "\n")

            # ------------------------------------------
            # Save CSV row
            # ------------------------------------------

            row = {
                "id": scenario_id,
                "product_name": final_state["product_name"],
                "buyer_cost": final_state["buyer_cost"],
                "seller_cost": final_state["seller_cost"],
                "buyer_target": final_state["buyer_target"],
                "seller_target": final_state["seller_target"],
                "buyer_emotion": buyer_emotion,
                "seller_emotion": seller_emotion,
                "success": metrics["success"],
                "turns": final_state["round"],
                "savings": metrics["savings"],
                "reward": metrics["reward"],
            }

            # Convert numpy types if present
            row = json.loads(json.dumps(row, default=json_converter))

            with open(csv_path, "a", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writerow(row)

            # ------------------------------------------
            # Update progress bar
            # ------------------------------------------

            pbar.update(1)

    pbar.close()

    print("\nSimulation finished.")
    print(f"Results CSV: {csv_path}")
    print(f"Histories JSONL: {jsonl_path}")


# ------------------------------------------------------------
# Run
# ------------------------------------------------------------

if __name__ == "__main__":
    main()