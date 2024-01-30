from typing import List
import json
import pandas
import re
import requests
import tqdm

URL_ENTRY = "https://fantasy.espn.com/tournament-challenge-bracket/2023/en/entry?entryID="

# bracket: str = "01|03|05|08|10|11|14|15|18|19|22|24|26|27|30|31|34|36|38|39|41|43|45|47|49|52|53|55|57|59|61|63|01|05|11|15|18|24|27|31|34|39|43|47|49|55|59|63|05|15|18|27|39|47|49|59|05|27|39|59|05|39|39"
# entryId: str = "86848038"

def get_bracket_info(entryId: str) -> dict:
    response: requests.Response = requests.get(URL_ENTRY + entryId, timeout=60)
    if response.status_code != 200:
        raise Exception(f"Failed to get EntryId '{entryId}'")

    bracketInfoSearch = re.search(r"espn\.fantasy\.maxpart\.config\.Entry = (.*);", response.text)
    if bracketInfoSearch is None:
        raise Exception("Failed to get Info")

    return json.loads(bracketInfoSearch.group(1))
#print(bracketInfo)
#print(bracketInfo["pct"])

submissions: pandas.DataFrame = pandas.read_csv("./data/2023/submissions.csv", dtype={"id": int, "score": float, "submitted": bool, "validated": bool})
"""
for index, row in tqdm.tqdm(submissions.iterrows()):
    info: dict = get_bracket_info(str(row["id"]))
    if info["p"] == 160:
        print(f"{entryId}: Points={bracketInfo['p']}, Percentile={round(bracketInfo['pct'], 2)}, BracketMatch={bracketInfo['ps'] == bracket}")

"""



solution: List[int] = []
with open("./data/2023/solution.txt", "r") as file:
    solution = [int(i) for i in file.readline().split("|")]

maxPoints: int = 0
for index, game in enumerate(solution):
    if game == -1:
        continue

    if index < 32:
        maxPoints += 10
print(f"Max = {maxPoints}")

count: int = [0, 0]
for index, row in submissions.iterrows():
    games: List[int] = [int(i) for i in row["bracket"].split("|")]

    points: int = 0
    for index, game in enumerate(games):
        if int(game) != solution[index]:
            continue

        if index < 32:
            points += 10

    if points == maxPoints:
        count[0] += 1
        if row["submitted"]:
            count[1] += 1
            print(row["email"])

print(f"Total = {count[0]}")
print(f"Submitted = {count[1]}")
