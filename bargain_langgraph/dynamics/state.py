from typing import TypedDict, List
import json

def load_json(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)

"""
Implements State to be passed to LangChain graph

Note: it contains both global and private (buyer and seller) information
Note: Only information available to player is used in transitions/apply_agent_action
Note: Assume seller is non-adaptive, and we look from buyer side
Note: seller_*_type: if "static" then * stays same over rounds, else changes according to emotion_discount.py
Note: * = emotion / discount above

Written by: Sunrit Chakraborty
"""

class State(TypedDict):

    # global information
    round: int
    max_rounds: int

    buyer_name: str
    seller_name: str

    product_name: str
    product_description: str
    product_category: str
    product_condition: str
    product_used: int
    avg_similar_price: float
    avg_new_price: float
    demand: int
    supply: int # assuming market conditions are known to both parties

    initial_offer: float | None # initial offer by seller
    current_offer_by: str | None # "buyer" or "seller"
    current_buyer_offer: float | None
    current_seller_offer: float | None
    last_buyer_offer: float | None
    last_seller_offer: float | None
    agreement_reached: bool
    breakdown: bool
    agreed_price: float | None

    # buyer information (not available to seller)
    buyer_personality: str
    buyer_background: str
    buyer_cost: float
    buyer_emotion: str
    buyer_discount: float

    # seller information (not available to buyer)
    seller_personality: str
    seller_background: str
    seller_cost: float
    seller_emotion: str
    seller_discount: float

    # buyer potentially makes inference on these
    infer_seller_cost: float | None
    infer_seller_emotion: str | None
    infer_seller_discount: float | None

    # information for transitions
    buyer_emotion_type: str      # "static" or "dynamic"
    buyer_discount_type: str     # "static" or "dynamic"
    buyer_inference: bool        # if True, then buyer makes inference on seller private info
    seller_emotion_type: str     # "static" or "dynamic"
    seller_discount_type: str    # "static" or "dynamic"

    # history of actions and conversations
    history: List[dict]
    last_message: str | None

# Note: for seller: "dynamic" means changing according to set transition (non-adaptive)
# Note: for buyer: "dynamic" would mean changing based on some policy depending on conversation (adaptive)

def get_initial_state(product_name,
                      buyer_name,
                      seller_name,
                      max_rounds=10,
                      seller_static=None,
                      buyer_static=None,
                      do_inference=False
                      )->State:
    # seller_static is list of what stays static, e.g. ["emotion", "discount"] means emotion & discount stays static

    # get product information
    scenario_path = f"bargain_langgraph/dynamics/scenarios/examples.json"
    scenarios = load_json(scenario_path)
    if product_name not in scenarios:
        raise ValueError(f"Scenario '{product_name}' not found")
    product = scenarios[product_name]

    # get buyer information
    profiles_path = "bargain_langgraph/dynamics/profiles/personas.json"
    profiles = load_json(profiles_path)
    if buyer_name not in profiles:
        raise ValueError(f"Profile with name = '{buyer_name}' not found (for buyer)")
    buyer = profiles[buyer_name]

    # get seller information
    if seller_name not in profiles:
        raise ValueError(f"Profile with name = '{seller_name}' not found (for seller)")
    seller = profiles[seller_name]

    # extract static/dynamic buyer seller
    if seller_static is None:
        seller_static = []
    if "emotion" in seller_static:
        seller_emotion_type = "static"
    else:
        seller_emotion_type = "dynamic"
    if "discount" in seller_static:
        seller_discount_type = "static"
    else:
        seller_discount_type = "dynamic"

    if buyer_static is None:
        buyer_static = []
    if "emotion" in buyer_static:
        buyer_emotion_type = "static"
    else:
        buyer_emotion_type = "dynamic"
    if "discount" in buyer_static:
        buyer_discount_type = "static"
    else:
        buyer_discount_type = "dynamic"
    if do_inference:
        buyer_inference = True
    else:
        buyer_inference = False

    # build the State
    state = State(
        round=0,
        max_rounds=max_rounds,
        buyer_name=buyer_name,
        seller_name=seller_name,
        product_name=product["name"],
        product_description=product["description"],
        product_category=product["category"],
        product_condition=product["condition"],
        product_used=product["used"],
        avg_similar_price=product["avg_similar_price"],
        avg_new_price=product["avg_new_price"],
        demand=product["demand"],
        supply=product["supply"],
        initial_offer=None,
        current_buyer_offer=None,
        current_seller_offer=None,
        current_offer_by=None,
        last_buyer_offer=None,
        last_seller_offer=None,
        agreement_reached=False,
        breakdown=False,
        agreed_price=None,
        buyer_personality=buyer["personality"],
        buyer_background=buyer["background"],
        buyer_cost=product["buyer_cost"],
        buyer_emotion=buyer["emotion"],
        buyer_discount=buyer["discount"],
        seller_personality=seller["personality"],
        seller_background=seller["background"],
        seller_cost=product["seller_cost"],
        seller_emotion=seller["emotion"],
        seller_discount=seller["discount"],
        infer_seller_cost=None,
        infer_seller_emotion=None,
        infer_seller_discount=None,
        buyer_emotion_type=buyer_emotion_type,
        buyer_discount_type=buyer_discount_type,
        buyer_inference=buyer_inference,
        seller_emotion_type=seller_emotion_type,
        seller_discount_type=seller_discount_type,
        history=[],
        last_message=None
    )

    return state

"""
Example usage:

initial_state = get_initial_state(product_name="Laptop001", 
                                  buyer_name="Ravi", 
                                  seller_name="Leah",
                                  max_rounds=10,
                                  seller_static=["emotion", "discount"],
                                  buyer_static=["emotion", "discount"],
                                  do_inference=False)
"""