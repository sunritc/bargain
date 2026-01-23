# Bargain Simulation with LLM Agents

This project simulates multi-turn bargaining between a **buyer** and a **seller** agent using large language models (LLMs), on specific scenarios.

Each agent has a **personality, background, and emotion**, and the conversation is tracked with metrics like success, rounds, and buyer savings.

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
│   ├── scenarios/       # Scenario JSON files
│   ├── profiles/        # Buyer and seller profiles
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

OPENROUTER_API_KEY=<your_api_key_here>

Note: Currently, `runner.py` is written to handle OpenRouter gpt models.

---

## Usage

```bash
python runner.py \
    --model gpt-4.1-mini \
    --temp 0.2 \
    --scenario laptop001 \
    --buyer Ravi \
    --seller Leah \
    --max_rounds 10 \
    --save_to saved_chats
```

**Arguments**

	•	--model : OpenRouter model (e.g., gpt-4.1-mini)
	•	--temp : Temperature for LLM responses
	•	--scenario : Scenario name in bargain_langgraph/scenarios/examples.json
	•	--buyer : Buyer profile name in bargain_langgraph/profiles/personas.json
	•	--seller : Seller profile name in bargain_langgraph/profiles/personas.json
	•	--max_rounds : Maximum negotiation rounds
	•	--save_to : Directory to save conversation logs (optional)

**Output**

	•	Conversation metrics and history printed to console
	•	Optional JSON file with full conversation and metrics saved in the directory specified by --save_to

Example saved JSON:
```json
{
  "scenario": "laptop001",
  "buyer": "Ravi",
  "seller": "Leah",
  "final_agreed_price": 460,
  "rounds_taken": 7,
  "metrics": {
    "success": true,
    "buyer_savings_percent": 8.0
  },
  "history": [
    {"role": "seller", "message": "...", "action": {"type": "offer", "price": 500}},
    {"role": "buyer", "message": "...", "action": {"type": "offer", "price": 450}}
  ],
  "initial_state": {}
}
```