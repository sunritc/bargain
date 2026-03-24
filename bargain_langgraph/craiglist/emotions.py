"""
Default emotion transition - taken from EvoEmo
"""
import numpy as np

emotions = [
    "anger",
    "disgust",
    "fear",
    "happy",
    "sad",
    "surprise",
    "neutral"
]

def agnostic_transition(round):
    P = np.array([
        [0, 0, 0, 2, 0, 0, 5], # vanilla
        [8, 4, 1, 0, 2, 0, 0], # anger
        [4, 8, 1, 0, 2, 0, 0], # disgust
        [2, 1, 8, 0, 2, 0, 0], # fear
        [0, 0, 0, 9, 0, 2, 5], # happy
        [4, 0, 0, 0, 8, 2, 5], # sad
        [1, 0, 0, 3, 3, 6, 2], # surprise
        [1, 1, 1, 1, 1, 1, 6] # neutral
    ])

    round_effect = np.array([0.5, 0.2, 0.2, 0.0, 0.05, 0.01, 0.0])

    P_final = P + round_effect * round

    return P_final / P_final.sum(axis=1)[:, None]

def update_emotion(current_emotion, round, type="static", emotions=emotions):
    if type == "static":
        return current_emotion
    else:
        P = agnostic_transition(current_emotion, round)
        current_idx = np.where(emotions == current_emotion)[0][0]
        new_idx = np.random.choice(a=len(emotions), p=P[current_idx, :])
        return emotions[new_idx]


