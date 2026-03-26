# Backend Architecture

## Goal
Provide a modular, production-ready backend structure for:
- Multi-format resume ingestion (PDF, DOCX, TXT)
- Job description text ingestion
- Text normalization
- Preprocessing
- NLP feature extraction

## Module Responsibilities

### API Layer
Path: `app/api`
- `routers/processing.py`: exposes processing endpoints.
- `routers/health.py`: liveness endpoint.

### Document Processing Layer
Path: `app/services/document_processing`
- `extractors/pdf_extractor.py`: PDF text extraction.
- `extractors/docx_extractor.py`: DOCX text extraction.
- `extractors/txt_extractor.py`: TXT extraction.
- `extractor_factory.py`: maps extension to extractor.
- `normalizer.py`: converts output to unified document schema.

### Preprocessing Layer
Path: `app/services/preprocessing`
- `cleaner.py`: lowercasing, special-char removal, tokenization, optional stopword removal.

### NLP + Feature Layer
Path: `app/services/nlp`
- `features.py`: baseline lexical features (token stats, lexical diversity, top keywords).

### Pipeline Layer
Path: `app/services/pipeline.py`
- Orchestrates extraction -> normalization -> preprocessing -> feature extraction.
- Shared flow for resume uploads and job description text.

### Schema Layer
Path: `app/schemas`
- `documents.py`: request/response contracts and standardized document model.

## Endpoint Contract

### POST `/v1/process/resume`
Input:
- multipart file (`.pdf`, `.docx`, `.txt`)

Output:
- standardized document
- cleaned text
- tokens
- extracted features

### POST `/v1/process/job-description`
Input JSON:
- `text`: string
- `options`: preprocessing options

Output:
- standardized document
- cleaned text
- tokens
- extracted features

## Extension Points
1. Add OCR parser in `document_processing/extractors`.
2. Add spaCy/transformer embeddings in `nlp`.
3. Persist processed outputs to database.
4. Add async worker queue for heavy parsing.
