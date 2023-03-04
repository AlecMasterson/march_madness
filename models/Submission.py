from dataclasses import dataclass, field
from typing import List

@dataclass
class Submission:
    bracket: str
    email: str
    id: str
    name: str
    percentile: float
    score: int
    rounds: List[dict] = field(default_factory=[])
