from io import BytesIO

from docx import Document

from app.services.document_processing.base import DocumentExtractor, ExtractionResult


class DOCXExtractor(DocumentExtractor):
    def extract(self, data: bytes) -> ExtractionResult:
        doc = Document(BytesIO(data))
        lines = [paragraph.text for paragraph in doc.paragraphs if paragraph.text]
        text = "\n".join(lines).strip()
        return ExtractionResult(text=text, metadata={"paragraphs": len(lines), "format": "docx"})
