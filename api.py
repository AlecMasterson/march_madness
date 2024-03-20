from ESPN import ESPN
from fastapi import FastAPI
from utils import LOGGER
import os

app = FastAPI()

@app.get("/get_token/{emailId}")
def get_code(emailId: int) -> str:
    email: str = f"{os.environ['EMAIL']}+{emailId}@gmail.com"
    LOGGER.info(f"{email}: Request for Token Received")

    with ESPN(email) as espn:
        espn.login()
        LOGGER.info(f"{email}: Token Received, Token='{espn.AuthToken}'")

        return espn.AuthToken
