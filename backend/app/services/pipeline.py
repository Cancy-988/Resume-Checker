from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings
from app.schemas.documents import PreprocessingOptions, ProcessedOutput
from app.services.document_processing.extractor_factory import get_extractor
from app.services.document_processing.normalizer import normalize_document
from app.services.nlp.features import extract_features
from app.services.preprocessing.cleaner import preprocess_text


async def process_resume_file(file: UploadFile) -> ProcessedOutput:
    extension = Path(file.filename or "").suffix.lower()
    extractor = get_extractor(extension)

    payload = await file.read()
    extraction = extractor.extract(payload)

    options = PreprocessingOptions(remove_stopwords=settings.enable_stopword_removal_default)
    document = normalize_document(
        source_type="resume",
        raw_text=extraction.text,
        original_filename=file.filename,
        metadata=extraction.metadata,
    )

    cleaned_text, tokens = preprocess_text(document.normalized_text, options)
    features = extract_features(tokens)

    return ProcessedOutput(document=document, cleaned_text=cleaned_text, tokens=tokens, features=features)


def process_job_description_text(text: str, options: PreprocessingOptions) -> ProcessedOutput:
    document = normalize_document(
        source_type="job_description",
        raw_text=text,
        original_filename=None,
        metadata={"format": "text"},
    )

    cleaned_text, tokens = preprocess_text(document.normalized_text, options)
    features = extract_features(tokens)

    return ProcessedOutput(document=document, cleaned_text=cleaned_text, tokens=tokens, features=features)
