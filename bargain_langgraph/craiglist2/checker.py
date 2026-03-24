import json


class CraiglistMessageChecker:

    def __init__(self, llm):
        self.llm = llm

    def _build_prompt(self, state, message, role):

        seller_offer = state.get("current_seller_offer")
        buyer_offer = state.get("current_buyer_offer")

        return  f"""
You are a strict parser for a bargaining conversation.

Your job is to extract the structured action from a message.

----------------------------------------
VALID ACTIONS
----------------------------------------
- offer
- accept
- walk-away
- stay

----------------------------------------
CRITICAL RULES
----------------------------------------
1. ACCEPT is only valid if:
   - The other party has made an offer.
   - You are fully agreeing to that offer exactly.
   - If the message mentions any number that is NOT equal to the other party's current offer,
     treat it as an offer instead of accept.

2. OFFER must include a clearly stated numeric price.
   - If the message proposes a price different from the other party's last offer → offer.
   - If no price is mentioned → stay.

3. WALK-AWAY only if the message clearly indicates leaving the negotiation.

4. Otherwise → stay.

----------------------------------------
PRICE RULES
----------------------------------------
- Extract the most relevant proposed price from the message.
- Ignore historical prices unless clearly reused.
- If multiple numbers → choose the intended offer.
- If unclear → price = null and action = "stay".

----------------------------------------
CONTEXT
----------------------------------------
Role: {role}
Seller current offer: {seller_offer}
Buyer current offer: {buyer_offer}

----------------------------------------
MESSAGE
----------------------------------------
{message}

----------------------------------------
OUTPUT FORMAT (STRICT JSON)
----------------------------------------
{{
  "action": "offer | accept | walk-away | stay",
  "price": number or null
}}
"""

    def parse(self, state, message, role):

        prompt = self._build_prompt(state, message, role)

        resp = self.llm.invoke([
            {"role": "system", "content": "You extract structured actions from negotiation messages."},
            {"role": "user", "content": prompt}
        ])

        try:
            parsed = json.loads(resp.content)
        except Exception:
            raise ValueError(f"Invalid JSON from checker: {resp.content}")

        return self._validate(parsed, state, role)

    # =========================
    # VALIDATION LAYER (CRITICAL)
    # =========================
    def _validate(self, parsed, state, role):
        """
        Validates and corrects the parsed action from LLM based on negotiation rules.
        Ensures:
          - Accept only if there is a valid other-party offer
          - Offer is within allowed bounds
          - Invalid offers become walk-away
        """
        action = parsed.get("action")
        price = parsed.get("price")

        valid_actions = {"offer", "accept", "walk-away", "stay"}
        if action not in valid_actions:
            return {"action": "stay", "price": None}

        # ------------------
        # ACCEPT VALIDATION
        # ------------------
        if action == "accept":
            if role == "buyer":
                other_offer = state.get("current_seller_offer")
            else:  # seller
                other_offer = state.get("current_buyer_offer")

            # Cannot accept if no other offer exists
            if other_offer is None:
                return {"action": "stay", "price": None}

            # If the message mentions a price that is NOT equal to the other party's offer, treat as offer
            if price is not None and price != other_offer:
                action = "offer"
            else:
                return {"action": "accept", "price": None}

        # ------------------
        # OFFER VALIDATION
        # ------------------
        if action == "offer":
            try:
                price = float(price)
            except Exception:
                return {"action": "stay", "price": None}

            # Must be positive
            if price <= 0:
                return {"action": "stay", "price": None}

            # Enforce bounds
            if role == "buyer":
                buyer_cost = state.get("buyer_cost")
                buyer_cost = buyer_cost if buyer_cost is not None else float("inf")

                seller_offer = state.get("current_seller_offer")
                seller_offer = seller_offer if seller_offer is not None else float("inf")

                max_price = min(buyer_cost, seller_offer)
                if price > max_price:
                    return {"action": "walk-away", "price": None}
            elif role == "seller":
                seller_cost = state.get("seller_cost")
                seller_cost = seller_cost if seller_cost is not None else 0

                buyer_offer = state.get("current_buyer_offer")
                buyer_offer = buyer_offer if buyer_offer is not None else 0

                min_price = max(seller_cost, buyer_offer)
                if price < min_price:
                    return {"action": "walk-away", "price": None}

            return {"action": "offer", "price": price}

        # ------------------
        # WALK-AWAY
        # ------------------
        if action == "walk-away":
            return {"action": "walk-away", "price": None}

        # ------------------
        # STAY
        # ------------------
        return {"action": "stay", "price": None}