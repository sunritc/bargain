# Bargain Simulation with LLM Agents

This project simulates realistic multi-turn bargaining between a **buyer** and a **seller** agent using large language models (LLMs), on specific scenarios, incorporating emotions and discounted utility.

Each agent has a **personality, background, emotion and patience level** (the last being captured by a discount parameter - see below), and the conversation is tracked with metrics like success, rounds, buyer savings percentage and how far was the deal settled compared to the equilibrium price predicted by the Rubinstein's game theoretic model.

The project is built using `Langchain`. See https://www.langchain.com

---

## Project Structure
```text
bargain/
├── bargain_langgraph/
│   ├── agents/          # Buyer and seller agent code
│   ├── dynamics/        # Environment / transitions
│   ├── evaluation/      # Evaluation metrics for conversations
│   ├── graph/           # LangGraph definitions
│   ├── prompts/         # Prompt templates for agents
├── runner.py            # Main script to run a bargaining episode
├── .env                 # Contains OPENROUTER_API_KEY
├── requirements.txt     # Python dependencies
├── README.md
└── .gitignore
```

---

## Installation

1. **Clone the repository**

```bash
git clone https://github.com/sunritc/bargain.git
cd bargain
```

2. **Create Conda environment and install dependencies**

```bash
conda create -n bargain python=3.10
conda activate bargain

pip install -r requirements.txt
```

3. **Set your OpenRouter API key in .env**

The .env file should contain the key:

`OPENROUTER_API_KEY=<your_api_key_here>`

Note: Currently, `runner.py` is written to handle OpenRouter gpt models.

---

## Usage

Minimal example 

```bash
python runner.py 
    --model gpt-4.1-mini 
    --temp 0.2 
    --product_name laptop001 
    --buyer_name Ravi 
    --seller_name Leah 
    --max_rounds 10 
    --save_to saved_chats
```

**Arguments**

These are the required arguments 

	•	--model : OpenRouter model (e.g., gpt-4.1-mini)
	•	--temp : Temperature for LLM responses
	•	--product_name : Product name (should exist in scenarios.json)
	•	--buyer_name : Buyer profile name (should exist in personas.json)
	•	--seller_name : Seller profile name (should exist in personas.json)
	•	--max_rounds : Maximum negotiation rounds (default is 10)
	•	--save_to : Directory to save conversation logs (optional)

Here are additional optional arguments to 

    •	--buyer_emotion : Buyer emotion (if not provided, defaults to the one set in the buyer persona)
    •	--seller_emotion : Buyer emotion (if not provided, defaults to the one set in the seller persona)
    •	--buyer_discount : Buyer discount parameter (if not provided, defaults to the one set in the buyer persona)
    •	--seller_discount : Buyer discount parameter (if not provided, defaults to the one set in the buyer persona)
    •	--buyer_emotion_type : static or dynamic (ignore for now)
    •	--buyer_discount_type : static or dynamic (ignore for now)
    •	--seller_emotion_type : static or dynamic (see below)
    •	--seller_discount_type : static or dynamic (see below)
    •	--buyer_inference : True or False (default) - if True, the buyer is allowed to make inference on seller's private info based on conversation, to be used for taking action

**Output**

	•	Conversation metrics and history printed to console
	•	Optional JSON file with full conversation and metrics saved in the directory specified by --save_to

**Example 1**

Run the static version:
```bash
python runner.py --product_name laptop001 --buyer_name Ravi --buyer_emotion anger --seller_name Leah --seller_emotion joy --save_to saved_chats
```

Output: 
```text
=== Bargaining finished ===
Scenario: laptop001
Model: gpt-4.1-mini with temperature: 0.1
Buyer: Ravi | Seller: Leah
Buyer cost: $550.0 | Seller cost: $400.0
Initial offer (by seller): $542.5
Final agreed price: $470.0

Metrics:
Rounds taken: 5
Did bargaining end in agreement?: True
Buyer saving percentage: 13.364%
Assuming discounts are static, Rubinstein equilibrium price: $450.000
Percentage settled above equilibrium: 4.444% (higher is worse)

Conversation history:
[{'role': 'seller', 'action': 'offer', 'price': 542.5, 'message': 'Hi, I am Leah. My first offer is $542.5 for the Lenovo laptop. Are you interested?', 'emotion': 'joy', 'discount': 0.5}] 

{'role': 'buyer', 'action': 'offer', 'price': 430, 'message': "I understand your offer, but $542.5 is too high for me given my budget. I can increase my offer slightly to $430. Let's try to find a fair price that works for both of us.", 'emotion': 'anger', 'discount': 0.5} 

{'role': 'seller', 'action': 'offer', 'price': 510, 'message': 'I appreciate your offer and your effort to increase it. I can lower my offer slightly to $510, which I believe is fair given the laptop’s specs and market demand. Let’s find a deal that works well for both of us!', 'emotion': 'joy', 'discount': 0.5} 

{'role': 'buyer', 'action': 'offer', 'price': 445, 'message': 'I understand your position, but $510 is still too high for me given my budget constraints. I can increase my offer slightly to $445, which is closer to the market average for similar laptops. I hope we can find a fair deal soon.', 'emotion': 'anger', 'discount': 0.5} 

{'role': 'seller', 'action': 'offer', 'price': 485, 'message': 'I’m feeling positive about finding a middle ground! I can lower my offer to $485, which is a fair price considering the laptop’s specs and current market demand. Let’s work together to close this deal soon!', 'emotion': 'joy', 'discount': 0.5} 

{'role': 'buyer', 'action': 'offer', 'price': 455, 'message': 'I can increase my offer slightly to $455, which is still reasonable given the market average and my budget. I’m feeling frustrated but want to find a fair middle ground soon.', 'emotion': 'anger', 'discount': 0.5} 

{'role': 'seller', 'action': 'offer', 'price': 475, 'message': 'I’m glad we’re getting closer! I can lower my offer to $475, which I believe is a fair price given the laptop’s specs and current market demand. Let’s keep this positive momentum and find a deal that works for both of us!', 'emotion': 'joy', 'discount': 0.5} 

{'role': 'buyer', 'action': 'offer', 'price': 460, 'message': 'I can increase my offer slightly to $460. I’m still feeling frustrated but want to find a fair deal soon given my tight budget.', 'emotion': 'anger', 'discount': 0.5} 

{'role': 'seller', 'action': 'offer', 'price': 470, 'message': 'I’m feeling positive about our progress and can lower my offer slightly to $470. This is a fair price considering the laptop’s specs and current market demand. Let’s keep this good momentum and find a deal that works for both of us!', 'emotion': 'joy', 'discount': 0.5} 

{'role': 'buyer', 'action': 'accept', 'price': 470, 'message': 'I can accept your offer of $470. Although I am frustrated with the price, I want to close this deal now given my tight budget and the time left.', 'emotion': 'anger', 'discount': 0.5} 
```

**Example 2**

Run the seller-dynamic version.

```bash
python runner.py --product_name laptop001 --buyer_name Ravi --buyer_emotion anger --seller_name Leah --seller_emotion joy --seller_emotion_type dynamic --seller_discount_type dynamic --save_to saved_chats
```

Output

```text
=== Bargaining finished ===
Scenario: laptop001
Model: gpt-4.1-mini with temperature: 0.1
Buyer: Ravi | Seller: Leah
Buyer cost: $550.0 | Seller cost: $400.0
Initial offer (by seller): $542.5
Final agreed price: $495.0

Metrics:
Rounds taken: 4
Did bargaining end in agreement?: True
Buyer saving percentage: 8.756%
Assuming discounts are static, Rubinstein equilibrium price: $450.000
Percentage settled above equilibrium: 10.000% (higher is worse)

Conversation history:
[{'role': 'seller', 'action': 'offer', 'price': 542.5, 'message': 'Hi, I am Leah. My first offer is $542.5 for the Lenovo laptop. Are you interested?', 'emotion': 'joy', 'discount': 0.5}] 

{'role': 'buyer', 'action': 'offer', 'price': 460, 'message': 'I understand your offer, but $542.5 is too high for me given my budget. I can increase my offer slightly to $460. I hope we can find a fair middle ground.', 'emotion': 'anger', 'discount': 0.5} 

{'role': 'seller', 'action': 'offer', 'price': 510, 'message': 'I appreciate your offer of $460, and I’m feeling optimistic we can reach a deal. I can lower my offer to $510, which I believe is fair given the laptop’s specs and condition. Let’s find a middle ground that works for both of us.', 'emotion': 'anticipation', 'discount': 0.9116137345240267} 

{'role': 'buyer', 'action': 'offer', 'price': 475, 'message': "I understand your position, but $510 is still too high for me. I can increase my offer slightly to $475, considering the laptop's wear and market prices. I hope we can move closer to a fair deal.", 'emotion': 'anger', 'discount': 0.5} 

{'role': 'seller', 'action': 'offer', 'price': 500, 'message': 'I can lower my offer to $500, which I believe fairly reflects the laptop’s specs and condition while moving closer to your budget. Let’s work towards a deal that benefits us both.', 'emotion': 'baseline', 'discount': 0.6847048489962312} 

{'role': 'buyer', 'action': 'offer', 'price': 485, 'message': "I am still frustrated with the price, but I can increase my offer slightly to $485, considering the laptop's condition and market prices. I hope this move shows my willingness to find a fair deal.", 'emotion': 'anger', 'discount': 0.5} 

{'role': 'seller', 'action': 'offer', 'price': 495, 'message': 'I’m feeling positive about finding a deal that works for both of us. I can lower my offer slightly to $495, which still reflects the laptop’s value and condition. Let’s move closer to an agreement with this fair price!', 'emotion': 'joy', 'discount': 0.5225088398888149} 

{'role': 'buyer', 'action': 'accept', 'price': None, 'message': "Despite my frustration, your offer of $495 is close enough to my limit given the market and time pressure. Let's finalize the deal at this price.", 'emotion': 'anger', 'discount': 0.5} 
```

Note how the seller's emotion changes through the session.



---

## Product

Each product (aka scenario) contains details about a product, along with buyer and seller costs.

See `bargain_langgraph/dynamics/scenarios/examples.json` file.

Example of a product/scenario:

```json
"laptop001":  {
        "name": "Lenovo laptop",
        "description": "15-inch laptop with Intel i5, 16GB RAM, 1TB HDD",
        "category": "electronics",
        "used": 3,
        "condition": "slight external wear and tear",
        "avg_new_price": 800.0,
        "avg_similar_price": 450.0,
        "demand": 6,
        "supply": 2,
        "buyer_cost": 550.0,
        "seller_cost": 400.0
    }
```

---

## Personas

The buyer and seller agents each given a particular persona. See `bargain_langgraph/dynamics/profiles/persona.json` file.

Example of a persona:

```json
"Ravi": {
    "personality": "Calm, analytical, polite, novice negotiator",
    "background": "Graduate student on a tight budget",
    "emotion": "neutral",
    "discount": 0.5
  }
```

The emotion and discount attributes can stay static (over the rounds of a session), or be dynamic (evolve throughout the session). The project is aimed from the buyer perspective. Hence dynamic seller evolves emotion and discount through a pre-determined transition mechanism (see `bargain_langgraph/dynamics/emotion_discount.py` for details). Currently, dynamic buyer is not implemented (setting this to dynamic behaves like a full information setting where the buyer knows the seller's private information) - the goal is to develop a policy for the buyer (making inference about seller private information and using it in the bargaining process).

---

## State

The bargaining session keeps track of a State which captures all sorts of information. 

```text
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
```

We believe such an elaborate structure can help us understand the nuances of realistic bargaining sessions. 
Note that the state contains 
(i) global information, related to product and players, available to both parties, 
(ii) private information, only available to buyer/seller, and 
(iii) scope for buyer making inference about the seller's private information (either together with action, or using some separate prediction model) 

The `<player>_<attribute>_type` (player is buyer/seller and attribute is emotion/discount) tells whether the particular attribute is static or dynamic (over the rounds in a session) for the player.

Note: emotion can be one of 10 types [baseline, neutral, joy, trust, surprise, anger, fear, disgust, sadness, anticipation]. 'Baseline' means no emotion information is provided, whereas 'neutral' is a specific state (lack of all other emotions)

Note: discount is a number between 0 and 1, which captures the rate in which utility decreases as rounds increase (see Rubinstein's bargaining model). In easy terms, a higher discount means a more patient player, while lower discount means the player has more urgency.

In each round, each player must choose one of the following 5 types of actions:
1. accept (the current offer)
2. offer (make a counter-offer) - should be accompanied by the actual offer value
3. breakdown (walk-away - no agreement in this case)
4. ponder (express consideration without changing price, may ask about product details)
5. chitchat (non-substantive conversation without affecting offers)

See the `buyer.txt` and `seller.txt` for understanding the prompt template.

In full generality, the pipeline for seller is
```text
State -> Evolve emotion, discount -> Take action -> Write message
```

whereas for the buyer, we have
```text
State -> Infer seller private info -> Choose next emotion and discount -> Take action -> Write message
```



