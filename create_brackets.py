from models.Game import Game
from models.Team import Team
from typing import List
import random
import pandas
import tqdm


__TEAMS: pandas.DataFrame = pandas.read_csv("./data/2023/teams.csv")


def build_bracket(teams: pandas.DataFrame, node: Game = Game()) -> Game:
    if node.depth == 5:
        node.team1 = Team(*teams.iloc[0].copy())
        teams.drop(teams.index[0], inplace=True)

        node.team2 = Team(*teams.iloc[0].copy())
        teams.drop(teams.index[0], inplace=True)
    else:
        node.left = build_bracket(teams, Game(depth=node.depth+1))
        node.team1 = node.left.winner
        node.right = build_bracket(teams, Game(depth=node.depth+1))
        node.team2 = node.right.winner

    node.winner = random.choices([node.team1, node.team2], k=1, weights=[node.team2.bracket_seed, node.team1.bracket_seed])[0]

    return node


def create_bracket(brackets: List[str]) -> str:
    bracket: str = None

    while bracket is None or bracket in brackets:
        bracket = to_string(build_bracket(__TEAMS.copy()))

    return bracket


def to_string(root: Game) -> str:
    def to_string(node: Game, level: int) -> str:
        if node.depth == level:
            return str(node.winner.bracket_id).zfill(2) if node.winner is not None else -1

        return f"{to_string(node.left, level)}|{to_string(node.right, level)}"

    return "|".join([to_string(root, 5-i) for i in range(6)])


if __name__ == "__main__":
    submissions: pandas.DataFrame = pandas.read_csv("./data/2023/submissions.csv", dtype={"id": int, "score": float, "submitted": bool, "validated": bool})

    emails: List[str] = []
    with open("./data/emails.txt", "r") as file:
        emails = list(set(line.strip() for line in file))

    for email in tqdm.tqdm(emails):
        count: int = len(submissions[submissions["email"] == email])

        for _ in range(25 - count):
            newSubmission = pandas.DataFrame([{
                "bracket": create_bracket(submissions["bracket"]),
                "email": email,
                "id": -1,
                "type": "WEIGHTED_SEED",
                "submitted": False,
                "validated": False,
                "score": 0.0
            }])

            submissions = pandas.concat([submissions, newSubmission], ignore_index=True)

    submissions.to_csv("./data/2023/submissions.csv", index=False)
