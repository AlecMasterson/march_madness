from typing import List
import json
import pandas
import requests

__CHALLENGE_ID = 240
__SEED_ORDER = [1, 16, 8, 9, 5, 12, 4, 13, 6, 11, 3, 14, 7, 10, 2, 15]
__YEAR = 2024


response: requests.Response = requests.get(f"https://gambit-api.fantasy.espn.com/apis/v1/propositions?challengeId={__CHALLENGE_ID}&platform=chui&view=chui_default")
data: List[dict] = response.json()
data: List[dict] = sorted(data, key=lambda x: (x["scoringPeriodId"], x["scoringPeriodMatchupId"]))

with open(f"./data/{__YEAR}/matchups.json", "w") as file:
    json.dump(data, file)
    file.close()

teams: List[dict] = []
for matchup in data:
    if matchup["scoringPeriodId"] != 1:
        continue

    for team in sorted(matchup["possibleOutcomes"], key=lambda x: x["regionSeed"]):
        teams.append({
            "bracket_id": ((team["regionId"] - 1) * 16) + __SEED_ORDER.index(team["regionSeed"]) + 1,
            "rank": int([x for x in team["mappings"] if x["type"] == "RANKING"][0]["value"]),
            "record": team["additionalInfo"],
            "region": team["regionId"],
            "seed": team["regionSeed"],
            "team_abbrev": team["abbrev"],
            "team_name": team["name"]
        })

df: pandas.DataFrame = pandas.DataFrame(data=teams).sort_values(by="bracket_id")
df.to_csv(f"./data/{__YEAR}/teams.csv", index=False)
