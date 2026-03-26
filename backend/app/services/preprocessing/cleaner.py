import re

from app.schemas.documents import PreprocessingOptions

DEFAULT_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "with",
}


def preprocess_text(text: str, options: PreprocessingOptions) -> tuple[str, list[str]]:
    if not text or not text.strip():
        raise ValueError("Input text is empty after extraction")

    working = text

    if options.lowercase:
        working = working.lower()

    if options.remove_special_characters:
        # Keep letters, numbers, and spaces only for stable downstream tokenization.
        working = re.sub(r"[^a-z0-9\s]", " ", working)

    working = re.sub(r"\s+", " ", working).strip()

    tokens = []
    if options.tokenize:
        tokens = [token for token in working.split(" ") if token]
    else:
        tokens = [working] if working else []

    if options.remove_stopwords:
        tokens = [token for token in tokens if token not in DEFAULT_STOPWORDS]

    cleaned_text = " ".join(tokens)
    return cleaned_text, tokens
