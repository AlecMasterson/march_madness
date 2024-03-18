from typing import List
import pandas
import requests

__CHALLENGE_ID = 240
__YEAR = 2024

response: requests.Response = requests.get(f"https://gambit-api.fantasy.espn.com/apis/v1/propositions?challengeId={__CHALLENGE_ID}&platform=chui&view=chui_default")
data: List[dict] = response.json()

matchups: List[dict] = []
for matchup in data:
    matchups.append({
        "id": matchup["id"],
        "scoringPeriodId": matchup["scoringPeriodId"],
        "scoringPeriodMatchupId": matchup["scoringPeriodMatchupId"]
    })

df: pandas.DataFrame = pandas.DataFrame(data=matchups).sort_values(by=["scoringPeriodId", "scoringPeriodMatchupId"])
df["bracket_id"] = range(1, len(df) + 1)
df.to_csv(f"./data/{__YEAR}/matchups.csv", index=False)

teams: List[dict] = []
for matchup in data:
    if matchup["scoringPeriodId"] != 1:
        continue

    for team in matchup["possibleOutcomes"]:
        teams.append({
            "bracket_id": ((team["regionId"] - 1) * 16) + team["regionSeed"],
            "id": team["id"],
            "rank": int([x for x in team["mappings"] if x["type"] == "RANKING"][0]["value"]),
            "record": team["additionalInfo"],
            "region": team["regionId"],
            "seed": team["regionSeed"],
            "team_abbrev": team["abbrev"],
            "team_name": team["name"]
        })

df: pandas.DataFrame = pandas.DataFrame(data=teams).sort_values(by="bracket_id")
df.to_csv(f"./data/{__YEAR}/teams.csv", index=False)
