from argparse import ArgumentParser
from concurrent.futures import as_completed, Future, ProcessPoolExecutor, wait
from ESPN import ESPN
from exceptions.EmailTakenException import EmailTakenException
from exceptions.InvalidEmailException import InvalidEmailException
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from tqdm import tqdm
from typing import List
from utils import LOGGER
import re


INPUT_EMAIL = "alecjmasterson+####@gmail.com"


def get_email_number(email: str) -> str:
    return re.search(r"\d+", email).group()


def register(email: str) -> tuple:
    message: str = ""

    try:
        with ESPN(email) as espn:
            espn.register()

        return (True, email, None)
    except EmailTakenException:
        return (True, email, "EMAIL TAKEN")
    except InvalidEmailException:
        message = "INVALID EMAIL"
    except NoSuchElementException:
        message = "NOSUCHELEMENT"
    except TimeoutException:
        message = "TIMEOUT"
    except Exception:
        message = "UNKNOWN"

    return (False, email, message)


def main(emails: List[str]) -> None:
    futures: List[Future] = []

    with ProcessPoolExecutor(max_workers=6) as executor:
        futures = [executor.submit(register, email) for email in emails]

        for _ in tqdm(as_completed(futures), total=len(futures)):
            pass

        wait(futures)

    results: List[tuple] = [future.result() for future in futures]

    existing = []
    with open("./data/emails.txt", "r") as file:
        existing = set(line.strip() for line in file)
    for result in [result for result in results if result[0]]:
        existing.add(result[1])
    with open("./data/emails.txt", "w") as file:
        def get_n(i):
            return int("".join(filter(str.isdigit, i)))
        existing = sorted(list(existing), key=get_n)
        file.writelines("\n".join(existing))

    failures: List[tuple] = [result for result in results if not result[0]]
    uniqueErrors = set(failure[-1] for failure in failures)
    result_dict = {error: [get_email_number(failure[1]) for failure in failures if failure[-1] == error] for error in uniqueErrors}

    LOGGER.info(result_dict)


# Most Recently Registered: 1500
if __name__ == "__main__":
    parser = ArgumentParser(description="Tool for Registering Email Accounts with ESPN")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--emails", dest="EMAILS", help="a list of emails to register, format ####", nargs="+", type=str)
    group.add_argument("--range", dest="RANGE", help="a range of emails to register, format ####:####", type=str)
    args = parser.parse_args()

    emails: List[str] = []
    if args.EMAILS is not None:
        emails = [INPUT_EMAIL.replace("####", email) for email in args.EMAILS]
    if args.RANGE is not None:
        temp: List[str] = args.RANGE.split(":")
        emails = [INPUT_EMAIL.replace("####", str(email)) for email in range(int(temp[0]), int(temp[1]))]

    if len(emails) > 0:
        LOGGER.info(f"Attempting to Register {len(emails)} Email(s) with ESPN")
        main(emails)
    else:
        LOGGER.warning("No Emails Provided to Register with ESPN")
