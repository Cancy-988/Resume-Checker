from dataclasses import dataclass


@dataclass
class ExtractionResult:
    text: str
    metadata: dict


class DocumentExtractor:
    def extract(self, data: bytes) -> ExtractionResult:
        raise NotImplementedError
