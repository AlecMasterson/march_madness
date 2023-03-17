from typing import List
import pandas

submissions: pandas.DataFrame = pandas.read_csv("./data/2023/submissions.csv", dtype={"id": int, "score": float, "submitted": bool, "validated": bool})

solution: List[int] = []
with open("./data/2023/solution_whatif1.txt", "r") as file:
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
            # print(row["email"])

print(f"Total = {count[0]}")
print(f"Submitted = {count[1]}")
