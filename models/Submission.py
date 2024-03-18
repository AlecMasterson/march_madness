from dataclasses import dataclass

@dataclass
class Submission:
    bracket: str
    email: str
    id: str
    score: float
    submitted: bool
    validated: bool
