from typing import List
import pandas
import requests

CHALLENGE_ID = 240
YEAR = 2024

response: requests.Response = requests.get(f"https://gambit-api.fantasy.espn.com/apis/v1/propositions?challengeId={CHALLENGE_ID}&platform=chui&view=chui_default")
data: List[dict] = response.json()

teams: List[dict] = []
for matchup in data:
    if len(matchup["possibleOutcomes"]) != 2:
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

df = pandas.DataFrame(data=teams).sort_values(by="bracket_id")
df.to_csv(f"./data/{YEAR}/teams.csv", index=False)
