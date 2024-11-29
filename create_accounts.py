from argparse import ArgumentParser
from ESPN import ESPN
from exceptions.EmailAvailabilityException import EmailAvailabilityException
from exceptions.EmailTakenException import EmailTakenException
from exceptions.RegistrationException import RegistrationException
from tqdm import tqdm
from typing import List, Set
from utils import LOGGER
import os


def register(email: str) -> bool:
    try:
        with ESPN(email) as espn:
            espn.register()

        return True
    except EmailAvailabilityException as e:
        LOGGER.error(f"{email}: Failed to Check Email Availability, {e}")
    except EmailTakenException:
        return True
    except RegistrationException as e:
        LOGGER.error(f"{email}: Failed to Register Email, {e}")
    except Exception as e:
        LOGGER.error(f"{email}: Unknown Error, {e}")

    return False


def main(emails: List[str]) -> None:
    with open("./data/emails.txt", "a+") as file:
        file.seek(0)

        emailsExisting: Set[str] = set(line.strip() for line in file)
        emailsFiltered: Set[str] = set([email for email in emails if email not in emailsExisting])

        for email in tqdm(emailsFiltered):
            if register(email):
                file.write(email + "\n")
                file.flush()

        file.close()


if __name__ == "__main__":
    parser = ArgumentParser(description="Tool for Registering Email Accounts with ESPN")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--emails", dest="EMAILS", help="a list of email ids to register, format ####", nargs="+", type=int)
    group.add_argument("--range", dest="RANGE", help="a range of email ids to register, format ####:####", type=str)
    args = parser.parse_args()

    try:
        email: str = os.environ["EMAIL"]
    except:
        raise Exception("Environment Variables Missing, Please Check Requirements in README")

    emails: List[str] = []
    if args.EMAILS is not None:
        emails = [email + f"+{i}@gmail.com" for i in args.EMAILS]
    if args.RANGE is not None:
        temp: List[str] = args.RANGE.split(":")
        emails = [email + f"+{i}@gmail.com" for i in range(int(temp[0]), int(temp[1]) + 1)]

    main(emails)
