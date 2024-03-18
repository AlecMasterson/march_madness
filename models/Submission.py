from dataclasses import dataclass

@dataclass
class Submission:
    bracket: str
    email: int
    id: str
    score: float
    submitted: bool
    validated: bool
