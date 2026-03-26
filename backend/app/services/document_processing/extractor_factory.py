from app.services.document_processing.base import DocumentExtractor
from app.services.document_processing.extractors.docx_extractor import DOCXExtractor
from app.services.document_processing.extractors.pdf_extractor import PDFExtractor
from app.services.document_processing.extractors.txt_extractor import TXTExtractor


EXTRACTOR_BY_EXTENSION: dict[str, DocumentExtractor] = {
    ".pdf": PDFExtractor(),
    ".docx": DOCXExtractor(),
    ".txt": TXTExtractor(),
}


def get_extractor(file_extension: str) -> DocumentExtractor:
    extractor = EXTRACTOR_BY_EXTENSION.get(file_extension.lower())
    if not extractor:
        supported = ", ".join(sorted(EXTRACTOR_BY_EXTENSION.keys()))
        raise ValueError(f"Unsupported file extension '{file_extension}'. Supported: {supported}")
    return extractor
