from argparse import ArgumentParser
from concurrent.futures import as_completed, Future, ProcessPoolExecutor, wait
from ESPN import ESPN, submit_bracket
from tqdm import tqdm
from typing import Any, List, Optional
from utils import LOGGER
import multiprocessing
import numpy
import os
import pandas
import queue
import requests
import threading
import time
from security import safe_requests


LOCK = multiprocessing.Lock()
SUBMISSIONS = pandas.read_csv("./data/2024/submissions.csv", dtype={"bracket": str, "email": int, "id": str, "score": float, "submitted": bool, "validated": bool})
WORKERS = [[i, True] for i in range(4)]


def main(df: pandas.DataFrame, emails: List[str]) -> None:
    results: List[List[tuple]] = []

    with ProcessPoolExecutor(max_workers=2) as executor:
        futures: List[Future] = [executor.submit(submit, 0, df, email) for email in emails]

        for future in tqdm(as_completed(futures), total=len(futures)):
            results.append(future.result())

    results: List[List[tuple]] = [future.result() for future in futures]
    for result in numpy.array(results).flatten():
        df.loc[result[0], "id"] = result[1]
        df.loc[result[0], "submitted"] = True


def submit(worker: int, df: pandas.DataFrame, emailId: str) -> List[tuple]:
    brackets: pandas.DataFrame = df[(df["email"] == int(emailId)) & (~df["submitted"])]
    email: str = f"masterson.march.madness+{emailId}@gmail.com"
    results: List[tuple] = []

    if len(brackets) == 0:
        return results

    response: requests.Response = safe_requests.get(f"http://localhost:800{worker}/get_token/{emailId}", timeout=30)
    if not response.ok or response.status_code != 200 or response.text == "":
        LOGGER.error(f"{email}: Failed to Get Token, {response.status_code} - {response.text}")

    for index, row in brackets.iterrows():
        try:
            results.append((index, submit_bracket(email, response.text, row["bracket"])))
        except:
            pass

    return results


def submit_wrapper(df: pandas.DataFrame, emailId: str, results) -> None:
    global SUBMISSIONS
    global WORKERS
    worker: int = -1

    while worker == -1:
        with LOCK:
            options: List[int] = [x[0] for x in WORKERS if x[1]]
            worker = options[0] if len(options) > 0 else -1
            if worker != -1:
                LOGGER.info(f"{emailId}: Locking Worker, Worker='{worker}'")
                WORKERS[worker][1] = False
        if worker == -1:
            time.sleep(1)

    temp: List[tuple] = []
    try:
        temp = submit(worker, df, emailId)
        results.put(temp)
    except Exception as e:
        LOGGER.error(f"{emailId}: Failed - {e}")
        pass

    with LOCK:
        for result in temp:
            SUBMISSIONS.loc[result[0], "id"] = result[1]
            SUBMISSIONS.loc[result[0], "submitted"] = True
        SUBMISSIONS.to_csv("./data/2024/submissions.csv", index=False)

        LOGGER.info(f"{emailId}: Unlocking Worker, Worker='{worker}'")
        WORKERS[worker][1] = True


if __name__ == "__main__":
    emailIds: List[str] = list(set([str(i) for i in SUBMISSIONS["email"] if i < 1001 and len(SUBMISSIONS[(SUBMISSIONS["email"] == int(i)) & (~SUBMISSIONS["submitted"])]) > 0]))
    results = queue.Queue()
    threads = []

    for emailId in emailIds:
        thread = threading.Thread(args=(SUBMISSIONS, emailId, results), target=submit_wrapper)
        thread.start()
        threads.append(thread)

    with tqdm(total=len(threads)) as pbar:
        for thread in threads:
            thread.join()
            pbar.update(1)

    """
    while not results.empty():
        for result in results.get():
            SUBMISSIONS.loc[result[0], "id"] = result[1]
            SUBMISSIONS.loc[result[0], "submitted"] = True

    SUBMISSIONS.to_csv("./data/2024/submissions.csv", index=False)
    """
