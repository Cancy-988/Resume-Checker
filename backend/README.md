# Resume-Job Matching Backend

Production-oriented modular backend scaffold for resume/job text processing.

## Architecture Layers

1. API Layer (`app/api`)
- Validates requests and routes operations.

2. Document Processing Layer (`app/services/document_processing`)
- Handles PDF, DOCX, and TXT extraction.
- Normalizes extracted output to a standard document shape.

3. Preprocessing Layer (`app/services/preprocessing`)
- Lowercases text.
- Removes special characters.
- Tokenizes text.
- Optionally removes stopwords.

4. NLP Feature Extraction Layer (`app/services/nlp`)
- Produces lightweight lexical features as baseline.
- Designed for extension to embeddings/NER/semantic match.

5. Pipeline Orchestration (`app/services/pipeline.py`)
- Connects extraction -> preprocessing -> feature extraction.

## API Endpoints

- `GET /health`
- `POST /v1/process/resume` (multipart upload: PDF/DOCX/TXT)
- `POST /v1/process/job-description` (JSON text input)

## Run

```bash
cd backend
pip install -e .
uvicorn app.main:app --reload
```

Open API docs: `http://127.0.0.1:8000/docs`
