from app.services.document_processing.base import DocumentExtractor, ExtractionResult


class TXTExtractor(DocumentExtractor):
    def extract(self, data: bytes) -> ExtractionResult:
        text = data.decode("utf-8", errors="ignore").strip()
        line_count = len([line for line in text.splitlines() if line.strip()])
        return ExtractionResult(text=text, metadata={"lines": line_count, "format": "txt"})
