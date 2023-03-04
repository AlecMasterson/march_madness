from dataclasses import dataclass

@dataclass
class Team:
    season: int
    region: str
    bracket_seed: int
    bracket_id: int
    team_name: str
    wins: int
    losses: int
    top25_wins: int
    top25_losses: int
    ppg: float
    opp_ppg: float
    bpi: int
