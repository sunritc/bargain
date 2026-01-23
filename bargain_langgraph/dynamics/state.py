from typing import TypedDict, List, Optional
"""
State maintained throughout the bargaining process, which evolves through actions of buyer and seller agents
Written by: Sunrit Chakraborty
"""
class BargainState(TypedDict):
    round: int
    max_rounds: int

    seller_initial_price: float
    buyer_target_price: float
    last_buyer_price: float
    last_seller_price: float
    agreed_price: Optional[float]

    price_gap: float # (last_seller_offer - last_buyer_offer)

    product: dict

    buyer_value: float
    seller_cost: float

    buyer_personality: str
    seller_personality: str

    history: List[dict]