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

    def __repr__(self):
        team1Str = self.team1.team_name if self.team1 is not None else ""
        team2Str = self.team2.team_name if self.team2 is not None else ""

        return f"{team1Str} vs. {team2Str}"

    def setter(self, dir: str, node: Game) -> Game:
        if dir == "L":
            self.left = node
        if dir == "R":
            self.right = node
        return node
