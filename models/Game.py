from __future__ import annotations
from dataclasses import dataclass
from models.Team import Team
from typing import Optional

@dataclass
class Game:

    depth: int
    left: Optional[Game] = None
    right: Optional[Game] = None
    team1: Optional[Team] = None
    team2: Optional[Team] = None
    winner: Optional[Team] = None

    def __init__(self, depth=0) -> None:
        self.depth = depth

    def __repr__(self) -> str:
        team1Str: str = self.team1.team_name if self.team1 is not None else "UNKNOWN"
        team2Str: str = self.team2.team_name if self.team2 is not None else "UNKNOWN"

        return f"{team1Str} vs. {team2Str}"

    def __str__(self) -> str:
        def to_string(node: Game, level: int) -> str:
            if node.depth == level:
                return str(node.winner.bracket_id).zfill(2) if node.winner is not None else ""

            return f"{to_string(node.left, level)}|{to_string(node.right, level)}"

        return "|".join([to_string(self, 5-i) for i in range(6-self.depth)])
