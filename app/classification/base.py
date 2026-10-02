from abc import ABC, abstractmethod
from app.models import Segment, ClassificationResult

class BaseClassifier(ABC):
    @abstractmethod
    def classify(self, segment: Segment) -> classified_segment | None:
        """Restituisce il giudizio, oppure None se i dati non bastano."""