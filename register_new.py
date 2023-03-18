from dotenv import load_dotenv
from exceptions.EmailTakenException import EmailTakenException
from tqdm import tqdm
from utils import LOGGER
import os
import requests

load_dotenv(dotenv_path="./.env")

try:
    __CONFIG = {
        "EMAIL": os.environ["EMAIL"],
        "NAME_FIRST": os.environ["NAME_FIRST"],
        "NAME_LAST": os.environ["NAME_LAST"],
        "PASSWORD": os.environ["PASSWORD"],
        "USERNAME": os.environ["USER_NAME"]
    }
except:
    raise Exception("Environment Variables Missing, Please Check Requirements in README")

__ENDPOINT_EMAIL_AVAILABILITY = "/validate"
__ENDPOINT_LOGIN = "/guest/login"
__ENDPOINT_REGISTER = "/guest/register"

__URL = "https://registerdisney.go.com/jgc/v8/client/ESPN-ONESITE.WEB-PROD"

__HEADERS = {"Content-Type": "application/json"}

__PARAMS_LOGIN = {
    "feature": "no-password-reuse",
    "langPref": "en-US"
}
__PARAMS_REGISTER = {
    "autogeneratePassword": False,
    "autogenerateUsername": False,
    "feature": "no-password-reuse",
    "langPref": "en-US"
}

__PAYLOAD_LOGIN = {
    # "loginValue": email
    "password": __CONFIG["PASSWORD"]
}
__PAYLOAD_REGISTER = {
    # "displayName": {"proposedDisplayName": username}
    "legalAssertions": ["gtou_ppv2_proxy"],
    "password": __CONFIG["PASSWORD"],
    "profile": {
        # "email": email
        "firstName": __CONFIG["NAME_FIRST"],
        "lastName": __CONFIG["NAME_LAST"],
        "region": "US"
        # "username": username
    }
}


def get_email(id: str) -> str:
    return __CONFIG["EMAIL"] + f"+{id}@gmail.com"


def check_availability(email: str) -> None:
    payload: dict = {"email": email}

    response: requests.Response = requests.post(__URL + __ENDPOINT_EMAIL_AVAILABILITY, json=payload)
    if response.status_code == 200:
         return

    if "ACCOUNT_FOUND" in response.text:
        raise EmailTakenException

    raise Exception(f"{email}: Failed to Check Email Availability")


def register(email: str, id: str) -> None:
    check_availability(email)

    payload: dict = __PAYLOAD_REGISTER.copy()
    payload["displayName"] = {"proposedDisplayName":  __CONFIG["USERNAME"] + id}
    payload["profile"]["email"] = email
    payload["profile"]["username"] =  __CONFIG["USERNAME"] + id

    response: requests.Response = requests.post(__URL + __ENDPOINT_REGISTER, json=payload, headers=__HEADERS, params=__PARAMS_REGISTER)
    if response.status_code != 200:
        raise Exception(f"{email}: Failed to Register: {response.text}")

    response: dict = response.json()

    try:
        for key in payload["profile"]:
            try:
                assert payload["profile"][key] == response["data"]["profile"][key]
            except:
                LOGGER.error(f"{email}: Failed to Assert Profile Key '{key}'")
                raise Exception

        try:
            assert payload["displayName"]["proposedDisplayName"] == response["data"]["displayName"]["displayName"]
            assert payload["displayName"]["proposedDisplayName"] == response["data"]["displayName"]["proposedDisplayName"]
        except:
            LOGGER.error(f"{email}: Failed to Assert Profile Key 'displayName'")
            raise Exception
    except:
        raise Exception(f"{email}: Profile Assertion Failed")


if __name__ == "__main__":
    for i in tqdm([str(i) for i in range(201)]):
        try:
            register(get_email(str(i)), str(i))
        except EmailTakenException:
            pass
        except Exception as e:
            LOGGER.error(f"{get_email(i)}: Failed to Register: {e}")
