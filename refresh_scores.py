from models.Submission import Submission
from typing import List
from util import get_score
import json

if __name__ == "__main__":
    SUBMISSIONS: List[Submission] = []
    with open("data/2022/submissions.json", "r") as f:
        SUBMISSIONS = json.load(f)
        f.close()

    for i, submission in enumerate(SUBMISSIONS):
        bracket: List[int] = [int(matchup) for matchup in submission["bracket"].split("|")]
        SUBMISSIONS[i].score = get_score(bracket)

    with open("data/2022/submissions.json", "w") as f:
        f.write(json.dumps(SUBMISSIONS))
        f.close()
