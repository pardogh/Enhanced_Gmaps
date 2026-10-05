from abc import ABC, abstractmethod
from app.models import ValhallaSegment, ClassifiedSegment

class BaseClassifier(ABC):
    @abstractmethod
    def classify(self, segment: ValhallaSegment) -> ClassifiedSegment | None:
        """Restituisce il giudizio, oppure None se i dati non bastano."""