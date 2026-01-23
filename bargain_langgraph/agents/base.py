class Agent:
    def act(self, state: dict) -> dict:
        """
        Given the current state, return an action:
        {"type": "accept"} or {"type": "offer", "price": float}
        """
        raise NotImplementedError