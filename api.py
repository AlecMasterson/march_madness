from ESPN import ESPN
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from utils import LOGGER
import os

app = FastAPI()

@app.exception_handler(Exception)
async def exception_handler(request, exc):
    return JSONResponse(content={"message": f"Internal Server Error - {type(exc)}"}, status_code=500)


@app.post("/create_email")
async def create_email(request: dict) -> None:
    LOGGER.info(f"{request['email']}: Request to Create Email")

    with ESPN(request["email"]) as espn:
        espn.register()
        LOGGER.info(f"{request['email']}: Email Created")


@app.get("/get_token/{emailId}")
async def get_code(emailId: int) -> str:
    email: str = f"{os.environ['EMAIL']}+{emailId}@gmail.com"
    LOGGER.info(f"{email}: Request for Token Received")

    with ESPN(email) as espn:
        espn.login()
        LOGGER.info(f"{email}: Token Received, Token='{espn.AuthToken}'")

        return espn.AuthToken
