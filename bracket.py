from models.Game import Game
from models.Team import Team

def traverse(node: Game) -> Game:
    if node.depth == 3:
        node.team1 = Team()
        node.team2 = Team()
        return

    Game(node.depth + 1)
    traverse(node.left)
