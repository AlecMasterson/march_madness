from ESPN import ESPN
from utils import LOGGER
from utils.multiworkers import multiworkers
import json
import requests


def check_availability(email: str) -> bool:
    headers: dict = {
        "Content-Type": "application/json"
    }
    payload: dict = {
        "email": email
    }
    url: str = "https://registerdisney.go.com/jgc/v8/client/ESPN-ONESITE.WEB-PROD/validate"

    response: requests.Response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=60)
    if not response.ok or response.status_code != 200:
        if "ACCOUNT_FOUND" in response.text:
            return False

        raise Exception(response.text)

    return True


@multiworkers
def create(worker: int, id: int) -> bool:
    email: str = f"masterson.march.madness+{id}@gmail.com"

    if not check_availability(email):
        return True

    response: requests.Reesponse = requests.post(f"http://localhost:800{worker}/create_email", data=json.dumps({"email": email}), timeout=60)
    if not response.ok or response.status_code != 200 or response.text == "":
        LOGGER.error(f"{email}: Failed to Create Email, {response.status_code} - {response.text}")
        return False

    return True

if __name__ == "__main__":
    emailIds = [[i, False] for i in range(200)]
    create(items=emailIds, workers=4)
    for id in [i for i in emailIds if not i[1]]:
        print(id[0])
