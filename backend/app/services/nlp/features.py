from collections import Counter

from app.schemas.documents import NLPFeatures


def extract_features(tokens: list[str], top_k: int = 10) -> NLPFeatures:
    if not tokens:
        return NLPFeatures(
            token_count=0,
            unique_token_count=0,
            lexical_diversity=0.0,
            top_keywords=[],
        )

    counts = Counter(tokens)
    token_count = len(tokens)
    unique_count = len(counts)
    diversity = unique_count / token_count if token_count else 0.0
    top_keywords = [token for token, _ in counts.most_common(top_k)]

    return NLPFeatures(
        token_count=token_count,
        unique_token_count=unique_count,
        lexical_diversity=round(diversity, 4),
        top_keywords=top_keywords,
    )
