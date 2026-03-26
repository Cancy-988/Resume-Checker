from io import BytesIO

import pdfplumber

from app.services.document_processing.base import DocumentExtractor, ExtractionResult


class PDFExtractor(DocumentExtractor):
    def extract(self, data: bytes) -> ExtractionResult:
        text_chunks: list[str] = []

        with pdfplumber.open(BytesIO(data)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text_chunks.append(page_text)

        text = "\n".join(text_chunks).strip()
        return ExtractionResult(text=text, metadata={"pages": len(text_chunks), "format": "pdf"})
