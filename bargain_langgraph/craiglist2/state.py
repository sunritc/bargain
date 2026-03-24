from typing import TypedDict, List
import json
import pandas as pd
from pathlib import Path

def load_json(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)

"""
This is specific to Craiglist Bargain dataset (scenarios)

Each scenario has product details (title, description, category and listing price)
So seller has already posted an ad for the product with the listing price

Buyer initiates conversation

Both buyer and seller have target price (seller target price is always listing price)
Note that this is target price, not the underlying reservation cost

For negotiation, buyer reservation price > seller cost
So, need to set up (construct) buyer and seller cost

seller_cost < 

Buyer is the agent, seller is simulated to be the human
"""

class CraiglistState(TypedDict):

    round: int
    max_rounds: int

    # buyer details
    buyer_target: int
    buyer_cost: int # set >= seller target
    buyer_emotion: str
    buyer_emotion_type: str

    # seller details
    seller_target: int
    seller_cost: int # set <= buyer target
    seller_emotion: str
    seller_emotion_type: str


    # product details
    product_name: str
    product_description: str
    product_category: str
    listing_price: int

    # negotiation state
    initial_offer: float | None  # initial offer by buyer
    current_offer_by: str | None  # "buyer" or "seller"
    current_buyer_offer: float | None
    current_seller_offer: float | None
    last_buyer_offer: float | None
    last_seller_offer: float | None
    price_gap : float | None
    agreement_reached: bool
    breakdown: bool
    agreed_price: float | None

    # history
    history: List[dict]
    last_message: str | None
    pending_message: str | None


def get_initial_craiglist_state(
        id: int,
        max_rounds=10,
        buyer_emotion="neutral",
        seller_emotion="neutral"
) -> CraiglistState:

    # get product information from craiglist csv
    data_path = Path(__file__).parent / "data" / "craigslist_bargain_scenarios_new.csv"
    df = pd.read_csv(data_path)

    row = df[df["id"] == id].iloc[0]
    product_name = row["title"]
    product_description = row["description"]
    product_category = row["category"]
    listing_price = row["listing_price"]

    # get buyer information
    buyer_target = row["buyer_target"]
    buyer_cost = row["buyer_cost"]
    buyer_emotion_type = "static"

    # get seller information
    seller_target = row["seller_target"]
    seller_cost = row["seller_cost"]
    seller_emotion_type = "static"

    # build the state
    state = CraiglistState(
        round=0,
        max_rounds=max_rounds,
        buyer_target=buyer_target,
        buyer_cost=buyer_cost,
        buyer_emotion=buyer_emotion,
        buyer_emotion_type=buyer_emotion_type,
        seller_target=seller_target,
        seller_cost=seller_cost,
        seller_emotion=seller_emotion,
        seller_emotion_type=seller_emotion_type,
        product_name=product_name,
        product_description=product_description,
        product_category=product_category,
        listing_price=listing_price,
        initial_offer=None,
        current_offer_by=None,
        current_buyer_offer=None,
        current_seller_offer=None,
        last_buyer_offer=None,
        last_seller_offer=None,
        price_gap=None,
        agreement_reached=False,
        breakdown=False,
        agreed_price=None,
        history=[],
        last_message=None,
        pending_message=None,
    )
    return state