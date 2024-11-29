from typing import List
import json
import pandas
import re
import requests
import tqdm

SUBMISSIONS = pandas.read_csv("./data/2024/submissions.csv", dtype={"bracket": str, "email": int, "id": str, "score": float, "submitted": bool, "validated": bool})

ROUND_1: str = "-1|-1|-1|-1|10|11|13|15|17|20|-1|-1|-1|-1|29|31|-1|-1|-1|-1|42|44|-1|-1|-1|-1|53|55|58|59|61|63"
# Kansas

count = 0
count2 = 0
for index, bracket in enumerate(list(SUBMISSIONS["bracket"])):
    bracketSplit: List[int] = [int(i) for i in bracket.split("|")]

    match = True
    for i, winner in enumerate([int(i) for i in ROUND_1.split("|")]):
        if winner == -1:
            continue
        if winner != bracketSplit[i]:
            match = False
    if match:
        count += 1
    if match and SUBMISSIONS["submitted"][index]:
        print(SUBMISSIONS["email"][index])
        count2 += 1
print(count)
print(count2)

"""
maxPoints: int = 0
for index, game in enumerate(ROUND_1):
    if game == -1:
        continue

    if index < 32:
        maxPoints += 10
    elif index < 48:
        maxPoints += 20
    elif index < 56:
        maxPoints += 40
    elif index < 60:
        maxPoints += 80
    elif index < 62:
        maxPoints += 160
    else:
        maxPoints += 320
print(f"Max = {maxPoints}\n")

count: dict = {}
count_submitted: dict = {}
elite_count: dict = {}
for index, row in submissions.iterrows():
    games: List[int] = [int(i) for i in row["bracket"].split("|")]

    points: int = 0
    elite: int = 0
    for index, game in enumerate(games):
        if int(game) != solution[index]:
            continue

        if index < 32:
            points += 10
        elif index < 48:
            points += 20
        elif index < 56:
            elite += 1
            points += 40
        elif index < 60:
            points += 80
        elif index < 62:
            points += 160
        else:
            points += 320

    if points not in count:
        count[points] = 0
    count[points] += 1

    if row["submitted"]:
        if points not in count_submitted:
            count_submitted[points] = 0
        count_submitted[points] += 1
        if elite not in elite_count:
            elite_count[elite] = 0
        elite_count[elite] += 1

x = sorted([i for i in count_submitted])[::-1]
for i in x:
    print(f"{i} = {count_submitted[i]}")
print()
x = sorted([i for i in elite_count])[::-1]
for i in x:
    print(f"{i} = {elite_count[i]}")
"""
