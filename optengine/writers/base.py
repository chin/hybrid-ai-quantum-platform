from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from optengine.recommendation import Recommendation


class RecommendationWriter(ABC):
    @abstractmethod
    def write(
        self,
        recommendation: Recommendation,
        output_dir: Path,
        run_name: str,
    ) -> Path:
        raise NotImplementedError
