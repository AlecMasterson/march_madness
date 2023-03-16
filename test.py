from typing import List
import pandas

df = pandas.DataFrame([{"A": -1}, {"A": -1}])
print((df["A"] == -1).all())
1/0

x: List[int] = []
with open("./data/emails.txt", "r") as file:
    x = sorted([int("".join(filter(str.isdigit, i))) for i in file.readlines()])

for i in range(1500):
    if i+1 not in x:
        print(i+1)
