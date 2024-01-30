from dacite import from_dict
from models.Game import Game
from models.Team import Team
from typing import List, Optional
import pandas
import random


REGIONS = ["WEST", "EAST", "SOUTH", "MIDWEST"]
SEED_DIST = [[1,16],[8,9],[5,12],[4,13],[6,11],[3,14],[7,10],[2,15]]
SOLUTION = pandas.read_csv("data/2022/solution.csv")
SOLUTION_WINNERS: List[int] = list(SOLUTION.sort_values(by="matchup").reset_index(drop=True)["winner"])
TEAMS = pandas.read_csv("data/2022/team_data.csv")


def get_score(submission: List[int]) -> int:
    score = 0

    score += sum(10 for index, winner in enumerate(SOLUTION_WINNERS[:32]) if int(submission[index]) == int(winner))
    score += sum(20 for index, winner in enumerate(SOLUTION_WINNERS[32:48]) if int(submission[index+32]) == int(winner))
    score += sum(40 for index, winner in enumerate(SOLUTION_WINNERS[48:56]) if int(submission[index+48]) == int(winner))
    score += sum(80 for index, winner in enumerate(SOLUTION_WINNERS[56:60]) if int(submission[index+56]) == int(winner))
    score += sum(160 for index, winner in enumerate(SOLUTION_WINNERS[60:62]) if int(submission[index+60]) == int(winner))
    score += sum(320 for index, winner in enumerate(SOLUTION_WINNERS[62:63]) if int(submission[index+62]) == int(winner))

    return score


def get_solution_by_matchup_id(matchup: int) -> Optional[dict]:
    solutions: List[dict] = SOLUTION[SOLUTION["matchup"] == matchup].to_dict(orient="records")
    assert len(solutions) <= 1

    return solutions[0] if len(solutions) == 1 else None


def get_team_by_bracket_id(bracket_id: int) -> Team:
    teams: List[dict] = TEAMS[TEAMS["bracket_id"] == bracket_id].to_dict(orient="records")
    assert len(teams) == 1

    return from_dict(data_class=Team, data=teams[0])


def get_team_by_seed(region: str, seed: int) -> Team:
    teams: List[dict] = TEAMS[(TEAMS["region"] == region) & (TEAMS["bracket_seed"] == seed)].to_dict(orient="records")
    assert len(teams) == 1

    return from_dict(data_class=Team, data=teams[0])


def bracket_build() -> Game:
    regions = REGIONS.copy()
    seeds = SEED_DIST.copy()

    def traverse(node: Game) -> Game:
        nonlocal regions
        nonlocal seeds

        if node.depth == 5:
            temp = seeds.pop(0)

            node.team1 = get_team_by_seed(regions[0], temp[0])
            node.team2 = get_team_by_seed(regions[0], temp[1])

            if len(seeds) == 0:
                regions = regions[1:]
                seeds = SEED_DIST.copy()

            return

        traverse(node.setter("L", Game(depth=node.depth+1)))
        traverse(node.setter("R", Game(depth=node.depth+1)))

        return node

    return traverse(Game())


# TODO: REVIEW
def bracket_solve(root: Game) -> str:
    def bracket_solve_level(game: Game, level: int) -> str:
        if game.depth == level:
            team1 = game.team1 if game.team1 is not None else game.left.winner
            team2 = game.team2 if game.team2 is not None else game.right.winner

            game.winner = random.choices([team1, team2], weights=[team2.bracket_seed, team1.bracket_seed], k=1)[0]

            return str(game.winner.bracket_id)

        return bracket_solve_level(game.left, level) + "|" + bracket_solve_level(game.right, level)

    return "|".join([bracket_solve_level(root, 5 - i) for i in range(6)])


def submission_to_json(submission: List[str]) -> List[dict]:
    root = bracket_build()

    def get_matchups(game: Game, level: int, matchups=[]) -> List[dict]:
        if game.depth == level:
            team1C: Team = {"bracket_seed": "TBD", "team_name": "TBD"}
            team1Score: int = 0
            team2C: Team = {"bracket_seed": "TBD", "team_name": "TBD"}
            team2Score: int = 0
            winnerC: str = "TBD"

            team1P: Team = game.team1 if game.team1 is not None else game.left.winner
            team2P: Team = game.team2 if game.team2 is not None else game.right.winner
            winnerP: Team = get_team_by_bracket_id(int(submission[len(matchups)]))
            game.winner = winnerP

            solution: Optional[dict] = get_solution_by_matchup_id(len(matchups))
            if solution is not None:
                team1C = get_team_by_bracket_id(int(solution["team1"]))
                team1Score: int = int(solution["team1_score"])
                team2C = get_team_by_bracket_id(int(solution["team2"]))
                team2Score: int = int(solution["team2_score"])
                winnerC: str = team1C.team_name if solution["team1_score"] > solution["team2_score"] else team2C.team_name

            matchups.append({
                "matchup": len(matchups),
                "points": 10 * pow(2, 5-level) if winnerC == winnerP.team_name else 0,
                "team1": {
                    "nameC": team1C.team_name,
                    "nameP": team1P.team_name,
                    "score": team1Score,
                    "seedC": team1C.bracket_seed,
                    "seedP": team1P.bracket_seed
                },
                "team2": {
                    "nameC": team2C.team_name,
                    "nameP": team2P.team_name,
                    "score": team2Score,
                    "seedC": team2C.bracket_seed,
                    "seedP": team2P.bracket_seed
                },
                "winnerC": winnerC,
                "winnerP": winnerP.team_name
            })

            return matchups

        get_matchups(game.left, level, matchups)
        get_matchups(game.right, level, matchups)

        return matchups

    response = [
        {"matchups": get_matchups(root, 5), "name": "Round of 64"},
        {"matchups": get_matchups(root, 4), "name": "Round of 32"},
        {"matchups": get_matchups(root, 3), "name": "Sweet 16"},
        {"matchups": get_matchups(root, 2), "name": "Elite 8"},
        {"matchups": get_matchups(root, 1), "name": "Final Four"},
        {"matchups": get_matchups(root, 0), "name": "Championship"}
    ]

    return [{**i, "points": sum(j["points"] for j in i["matchups"])} for i in response]
