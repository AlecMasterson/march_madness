from typing import List
import json
import pandas

__YEAR = "2024"

__MATCHUPS: List[dict] = []
with open(f"./data/{__YEAR}/matchups.json", "r") as file:
    __MATCHUPS = json.load(file)
    file.close()
__TEAMS: pandas.DataFrame = pandas.read_csv(f"data/{__YEAR}/teams.csv")


def build_submission_payload(bracket: str) -> dict:
    picks = []
    for index, winner in enumerate(bracket.split("|")):
        matchup: dict = __MATCHUPS[index]
        name: str = __TEAMS.loc[__TEAMS["bracket_id"] == int(winner), "team_name"].values[0]
        outcomeId: str = [x for x in matchup["possibleOutcomes"] if x["name"] == name][0]["id"]

        picks.append({
            "outcomesPicked": [{
                "outcomeId": outcomeId
            }],
            "propositionId": matchup["id"]
        })

    return {
        "challengeId": 240,
        "picks": picks,
        "scoringFormatId": 5,
        "tiebreakAnswers": [{
            "answer": 127,
            "tiebreakQuestionId": "a498a3e0-c12d-11ee-b568-d9cd047f74cf"
        }]
    }
