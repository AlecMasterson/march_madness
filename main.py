from dacite import from_dict
from fastapi import FastAPI
from models.Submission import Submission
from typing import List
from util import get_score, submission_to_json
import json

def get_submissions() -> List[Submission]:
    submissions: List[dict] = []
    with open("data/2022/submissions.json", "r") as f:
        submissions = json.load(f)
        f.close()

    return list(map(lambda x: Submission(**x), submissions))

app = FastAPI()

@app.get("/brackets")
async def root():
    submissions: List[Submission] = sorted(get_submissions(), key=lambda x: x.score, reverse=True)[:10]
    for submission in submissions:
        submission.rounds = submission_to_json(submission.bracket.split("|"))

    return submissions
