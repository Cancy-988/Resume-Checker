import re

from app.schemas.documents import StandardizedDocument


def normalize_document(
    *,
    source_type: str,
    raw_text: str,
    original_filename: str | None,
    metadata: dict,
) -> StandardizedDocument:
    compact = re.sub(r"\s+", " ", raw_text).strip()
    return StandardizedDocument(
        source_type=source_type,
        original_filename=original_filename,
        raw_text=raw_text,
        normalized_text=compact,
        metadata=metadata,
    )
