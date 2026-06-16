FRUSTRATION_TERMS = {
    "ridiculous": 0.85,
    "angry": 0.8,
    "waiting": 0.55,
    "complaint": 0.62,
    "useless": 0.9,
    "human": 0.75,
    "manager": 0.72,
    "3 days": 0.88,
}


def score_frustration(text: str) -> float:
    lower = text.lower()
    scores = [score for term, score in FRUSTRATION_TERMS.items() if term in lower]
    return max(scores, default=0.12)
