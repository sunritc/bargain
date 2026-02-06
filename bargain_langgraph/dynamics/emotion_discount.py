import numpy as np

"""
Emotion, Discount transition structure for seller

p(delta|.) = Beta(mu * kappa, (1-mu)*kappa)
mu = (1-rho) sigma(a) + rho delta_last
a = beta0 + beta1 (1-t/T) + beta2 (current_offer - seller_cost) / (buyer_cost - seller_cost))
sigma is the logistic link function
"""

def update_discount(current_discount,
                    round,
                    max_rounds,
                    current_offer,
                    seller_cost,
                    buyer_cost,
                    seller_params=None):
    # default params
    if seller_params is None:
        seller_params = {
            "beta0": 0.2,
            "beta1": 0.5,
            "beta2": 0.3,
            "rho": 0.5,
            "kappa": 0.9
        }

    beta0=seller_params["beta0"]
    beta1=seller_params["beta1"]
    beta2=seller_params["beta2"]
    rho=seller_params["rho"]
    kappa=seller_params["kappa"]

    a = beta0 + beta1 * (1- round/max_rounds)
    a += + beta2 * (current_offer - seller_cost) / (buyer_cost - seller_cost)
    mu = (1 - rho) / (1 + np.exp(-a)) + rho * current_discount
    b1 = mu * kappa
    b2 = (1 - mu) * kappa
    delta = np.random.beta(b1, b2)
    return delta

def update_emotion(delta):
    emotions = [
        "baseline",
        "neutral",
        "joy",
        "trust",
        "fear",
        "surprise",
        "sadness",
        "disgust",
        "anger",
        "anticipation"
    ]

    # for 0 < delta < 0.3
    p1 = [10, 0, 0, 0, 4, 2, 3, 3, 10, 5]
    p1 = np.array(p1) / np.sum(p1)

    # for 0.3 < delta < 0.7
    p2 = [10, 6, 1, 5, 2, 1, 3, 2, 4, 2]
    p2 = np.array(p2) / np.sum(p2)

    # for 0.7 < delta < 1.0
    p3 = [10, 1, 5, 4, 1, 3, 1, 0, 0, 4]
    p3 = np.array(p3) / np.sum(p3)

    if delta < 0.3:
        idx = np.random.choice(len(emotions), p=p1)
    elif delta < 0.7:
        idx = np.random.choice(len(emotions), p=p2)
    else:
        idx = np.random.choice(len(emotions), p=p3)
    return emotions[idx]





