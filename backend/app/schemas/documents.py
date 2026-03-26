from typing import Any

from pydantic import BaseModel, Field


class PreprocessingOptions(BaseModel):
    lowercase: bool = True
    remove_special_characters: bool = True
    tokenize: bool = True
    remove_stopwords: bool = False


class JobDescriptionRequest(BaseModel):
    text: str = Field(min_length=1)
    options: PreprocessingOptions = Field(default_factory=PreprocessingOptions)


class StandardizedDocument(BaseModel):
    source_type: str
    original_filename: str | None = None
    raw_text: str
    normalized_text: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class NLPFeatures(BaseModel):
    token_count: int
    unique_token_count: int
    lexical_diversity: float
    top_keywords: list[str]


class ProcessedOutput(BaseModel):
    document: StandardizedDocument
    cleaned_text: str
    tokens: list[str]
    features: NLPFeatures
