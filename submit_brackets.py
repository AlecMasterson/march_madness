from ESPN import ESPN
from typing import List
import pandas
import tqdm

if __name__ == "__main__":
    submissions = pandas.read_csv("./data/2023/submissions.csv")

    emails: List[str] = list(set(submissions["email"]))

    for email in tqdm.tqdm(emails):
        if email != "alecjmasterson+3@gmail.com":
            continue
        with ESPN(email) as espn:
            espn.login()
            for index, row in submissions[submissions["email"] == email].iterrows():
                if row["submitted"]:
                    continue
                if not pandas.isna(row["id"]):
                    espn.submit(row["bracket"], row["id"])
                else:
                    espn.submit(row["bracket"])
                row["submitted"] = True
