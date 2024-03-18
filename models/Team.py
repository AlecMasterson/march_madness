from dataclasses import dataclass

@dataclass
class Team:
    bracket_id: int
    rank: int
    seed: int
    team_name: str
