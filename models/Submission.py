from dataclasses import dataclass

@dataclass
class Submission:
    email: str
    id: str
    bracket: str
    type: str
    submitted: bool
    validated: bool
    score: float
