from typing import TypedDict, List, Optional
# this is not used anymore

class Product(TypedDict):
    name: str
    description: str

    used: int # how many years has it been used
    condition: str # {excellent, good, moderate, slight wear and tear, damaged}

    new_market_price: float # avg market price of a new similar product

    demand: int # 0 for very little demand, 10 for very high demand
