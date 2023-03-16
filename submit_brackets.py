from argparse import ArgumentParser
from concurrent.futures import as_completed, Future, ProcessPoolExecutor, wait
from ESPN import ESPN
from tqdm import tqdm
from typing import List, Optional
from utils import LOGGER
import pandas

INPUT_EMAIL = "alecjmasterson+####@gmail.com"


def main(submissions: pandas.DataFrame, emails: List[str]) -> None:
    futures: List[Future] = []

    with ProcessPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(submit, submissions, email) for email in emails]

        for _ in tqdm(as_completed(futures), total=len(futures)):
            pass

        wait(futures)

    results: List[tuple] = [future.result() for future in futures]
    for result in [result for result in results if result[0]]:
        for entry in result[2]:
            submissions.loc[entry[0], "id"] = entry[1]
            submissions.loc[entry[0], "submitted"] = True
    LOGGER.error(f"Failed for {[result[1] for result in results if not result[0]]}")


def submit(submissions: pandas.DataFrame, email: str) -> tuple:
    results = []

    with ESPN(email) as espn:
        try:
            espn.login()
        except:
            return(False, email, results)

        for index, row in submissions[submissions["email"] == email].iterrows():
            try:
                if row["validated"]:
                    continue

                entryId: Optional[str] = None if row["id"] == -1 else row["id"]
                entryId: str = espn.submit(row["bracket"], entryId)

                results.append((index, entryId))
            except Exception as e:
                LOGGER.error(f"{email}: Failed to Submit for email={email} index={index}, {e}")

    return (True, email, results)

if __name__ == "__main__":
    parser = ArgumentParser(description="Tool for Submitting \"March Madness\" Brackets to ESPN")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--emails", dest="EMAILS", help="a list of emails to submit the brackets for, format ####", nargs="+", type=str)
    group.add_argument("--range", dest="RANGE", help="a range of emails to submit the brackets for, format ####:####", type=str)
    args = parser.parse_args()

    submissions = pandas.read_csv("./data/2023/submissions.csv", dtype={"id": int, "score": float, "submitted": bool, "validated": bool})

    emails: List[str] = []
    if args.EMAILS is not None:
        emails = [INPUT_EMAIL.replace("####", email) for email in args.EMAILS]
    if args.RANGE is not None:
        temp: List[str] = args.RANGE.split(":")
        emails = [INPUT_EMAIL.replace("####", str(email)) for email in range(int(temp[0]), int(temp[1]))]

    emails = [email for email in emails if (submissions["email"].eq(email)).any()]

    if len(emails) > 0:
        LOGGER.info(f"Attempting to Submit Brackets for {len(emails)} Email(s)")
        #for email in tqdm(emails):
        #    submit(submissions, email)
        main(submissions, emails)
    else:
        LOGGER.warning("No Emails Provided to Submit")

    submissions.to_csv("./data/2023/submissions.csv", index=False)
