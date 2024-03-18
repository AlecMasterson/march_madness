from models.Game import Game
from models.Team import Team
import random
import pandas
import tqdm

__SUBMISSIONS: pandas.DataFrame = pandas.read_csv("./data/2024/submissions.csv")
__TEAMS: pandas.DataFrame = pandas.read_csv("./data/2024/teams.csv")


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

    node.winner = random.choices([node.team1, node.team2], k=1, weights=[node.team2.seed, node.team1.seed])[0]

    return node


if __name__ == "__main__":
    submissions: pandas.DataFrame = __SUBMISSIONS.copy()
    submissions["submitted"] = submissions["submitted"].astype(bool)
    submissions["validated"] = submissions["validated"].astype(bool)

    for i in tqdm.tqdm(range(1)):
        toMake: int = 25 - len(submissions[submissions["email"] == i+1])

        if toMake == 0:
            continue
        elif toMake < 0:
            raise Exception(f"Email '{i}' Has Too Many Brackets")

        for _ in range(toMake):
            bracket: str = ""
            while bracket == "" or bracket in submissions["bracket"]:
                bracket = str(build_bracket(__TEAMS.copy()))

            newSubmission: pandas.DataFrame = pandas.DataFrame([{
                "bracket": bracket,
                "email": i+1,
                "id": "",
                "score": 0.0,
                "submitted": False,
                "validated": False
            }])
            newSubmission["submitted"] = newSubmission["submitted"].astype(bool)
            newSubmission["validated"] = newSubmission["validated"].astype(bool)

            submissions: pandas.DataFrame = pandas.concat([submissions, newSubmission], ignore_index=True)

        submissions.to_csv("./data/2024/submissions.csv", index=False)
