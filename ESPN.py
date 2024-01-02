from dotenv import load_dotenv
from exceptions.BracketSubmissionException import BracketSubmissionException
from exceptions.EmailTakenException import EmailTakenException
from exceptions.EntryIdMismatchException import EntryIdMismatchException
from GMail import get_code
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from typing import List, Optional
from utils import LOGGER
import os
import re
import requests
import time
from security import safe_requests

load_dotenv(dotenv_path="./.env")


ELEMENT_IFRAME = "//iframe[@name='oneid-iframe']"
ELEMENT_INPUT_BUTTON_SIGNUP = "//button[@id='BtnCreateAccount']"
ELEMENT_INPUT_BUTTON_SUBMIT = "//button[@id='BtnSubmit']"
ELEMENT_INPUT_TEXT_CODE = "//input[@id='InputRedeemOTP']"
ELEMENT_INPUT_TEXT_EMAIL = "//input[@type='email']"
ELEMENT_INPUT_TEXT_NAME_FIRST = "//input[@id='InputFirstName']"
ELEMENT_INPUT_TEXT_NAME_LAST = "//input[@id='InputLastName']"
ELEMENT_INPUT_TEXT_PASSWORD = "//input[@type='password']"

PARAMS_BRACKET_CREATE = {"r": "entry", "t1": 72, "t2": 65}

URL_ENDPOINT_BRACKET_CREATE = "/createOrUpdateEntry"
URL_ENDPOINT_BRACKET_ENTRY = "/entry\?entryID=(\d+)"

URL_TOURNAMENT_CHALLENGE = "https://fantasy.espn.com/tournament-challenge-bracket/2023/en"
URL_VALIDATE_EMAIL = "https://registerdisney.go.com/jgc/v8/client/ESPN-ONESITE.WEB-PROD/validate"

class ESPN:


    AuthToken: str
    Email: str
    __Driver: WebDriver
    __DriverWait: WebDriverWait

    __CONFIG = {}

    __ENDPOINT_EMAIL_AVAILABILITY = "/validate"
    __ENDPOINT_REGISTER = "/guest/register"

    __HEADERS = {
        "Content-Type": "application/json"
    }

    __PARAMS_REGISTER = {
        "autogeneratePassword": False,
        "autogenerateUsername": False,
        "feature": "no-password-reuse",
        "langPref": "en-US"
    }

    __PAYLOAD_REGISTER = {
        # "displayName": {"proposedDisplayName": username}
        "legalAssertions": ["gtou_ppv2_proxy"],
        # "password": password,
        "profile": {
            # "email": email
            # "firstName": firstName,
            # "lastName": lastName,
            "region": "US"
            # "username": username
        }
    }

    __URL = "https://registerdisney.go.com/jgc/v8/client/ESPN-ONESITE.WEB-PROD"


    def __init__(self, email: str):
        try:
            self.__CONFIG = {
                "EMAIL": os.environ["EMAIL"],
                "NAME_FIRST": os.environ["NAME_FIRST"],
                "NAME_LAST": os.environ["NAME_LAST"],
                "PASSWORD": os.environ["PASSWORD"],
                "USERNAME": os.environ["USER_NAME"]
            }

            self.__PAYLOAD_REGISTER["password"] = self.__CONFIG["PASSWORD"]
            self.__PAYLOAD_REGISTER["profile"]["firstName"] = self.__CONFIG["NAME_FIRST"]
            self.__PAYLOAD_REGISTER["profile"]["lastName"] = self.__CONFIG["NAME_LAST"]
        except:
            raise Exception("Environment Variables Missing, Please Check Requirements in README")

        self.Email = email


    def __enter__(self):
        self.__Driver = self.__create_driver()
        self.__DriverWait = WebDriverWait(self.__Driver, timeout=10)

        return self


    def __exit__(self, *_):
        self.__Driver.close()
        self.__Driver.quit()


    def __create_driver(self) -> WebDriver:
        """
        Create a Selenium WebDriver instance to navigate ESPN.
        The instance will have headless mode enabled to prevent unnecessary rendering.

        Returns
        -------
        WebDriver
            A Selenium WebDriver instance to navigate ESPN.
        """
        driver_options: Options = Options()
        driver_options.add_argument("--disable-dev-shm-usage")
        driver_options.add_argument("--headless")
        driver_options.add_argument("--incognito")
        driver_options.add_argument('--log-level=3')
        driver_options.add_argument('--no-sandbox')

        return webdriver.Chrome(options=driver_options)


    def check_availability(self) -> None:
        payload: dict = {"email": self.Email}
        url: str = self.__URL + self.__ENDPOINT_EMAIL_AVAILABILITY

        response: requests.Response = requests.post(url, json=payload)
        if response.ok and response.status_code == 200:
            return

        if "ACCOUNT_FOUND" in response.text:
            raise EmailTakenException

        raise Exception(f"{self.Email}: Failed to Check Email Availability, {response.text}")


    def get_element(self, xpath: str, isInput: bool = True) -> WebElement:
        """
        Find a single element in the given WebDriver context via an XPATH.
        Verifies that the element is displayed and (if an input element) is enabled.

        Parameters
        ----------
        xpath : str
            An XPATH used to search for the desired element.
        isInput : bool, optional (default True)
            Flag to indicate if the desired element is an input.

        Returns
        -------
        WebElement
            The desired element.

        Raises
        ------
        NoSuchElementException
            If the desired element is not found, not displayed, or (if an input element) not enabled.
        """
        try:
            elements: List[WebElement] = self.__Driver.find_elements(by=By.XPATH, value=xpath)
            assert len(elements) == 1 and elements[0].is_displayed() and (elements[0].is_enabled() if isInput else True)

            return elements[0]
        except:
            raise NoSuchElementException(xpath)


    def login(self) -> None:
        """
        Login to ESPN with the email address to obtain the AuthToken for API interacion.
        """
        self.__Driver.get(__URL_LOGIN)
        time.sleep(1)

         # Change the context of the WebDriver to the iFrame containing the login form.
        elementIFrame: WebElement = self.get_element(ELEMENT_IFRAME, isInput=False)
        self.__Driver.switch_to.frame(elementIFrame)

        # Enter the login form data for the account.
        self.get_element(ELEMENT_INPUT_TEXT_EMAIL).send_keys(self.Email)
        self.get_element(ELEMENT_INPUT_TEXT_PASSWORD).send_keys(INPUT_PASSWORD)
        time.sleep(1)

        # Submit the login form.
        self.get_element(ELEMENT_INPUT_BUTTON_SUBMIT).click()

        try:
            # Wait to see if an additional code is required for login.
            # If not required, this will quietly throw a TimeoutException.
            self.__DriverWait.until(EC.presence_of_element_located((By.XPATH, ELEMENT_INPUT_TEXT_CODE)))
            # LOGGER.warning(f"{self.Email}: Code Required for Login")

            # Retrieve the code from GMail and enter the form data.
            self.get_element(ELEMENT_INPUT_TEXT_CODE).send_keys(get_code(self.Email))
            time.sleep(1)

            # Submit the code form.
            self.get_element(ELEMENT_INPUT_BUTTON_SUBMIT).click()
        except TimeoutException:
            pass
        except Exception as e:
            LOGGER.error(f"{self.Email}: Failed to Provide Code, {e}")
            pass

        # Wait for the page to change to give confirmation.
        self.__DriverWait.until(EC.url_changes(__URL_LOGIN))
        time.sleep(1)

        # Update the AuthToken for this ESPN account to allow API interactions.
        self.AuthToken = self.__Driver.get_cookie("espn_s2")["value"]


    def register(self) -> None:
        self.check_availability()

        payload: dict = self.__PAYLOAD_REGISTER.copy()
        payload["displayName"] = {"proposedDisplayName": self.__CONFIG["USERNAME"] + id}
        payload["profile"]["email"] = self.Email
        payload["profile"]["username"] = self.__CONFIG["USERNAME"] + id

        url: str = self.__URL + self.__ENDPOINT_REGISTER

        response: requests.Response = requests.post(url, json=payload, headers=self.__HEADERS, params=self.__PARAMS_REGISTER)
        if not response.ok or response.status_code != 200:
            raise Exception(f"{self.Email}: Failed to Register, {response.text}")


    def submit(self, bracket: str, entryId: Optional[int]) -> int:
        """
        Submit a bracket to ESPN.

        Parameters
        ----------
        bracket : str
        entryId : Optional[int]

        Returns
        -------
        int
            The EntryId associated with the bracket that was submitted.

        Raises
        ------
        EntryIdMismatchException
        BracketSubmissionException
        """
        headers: dict = {"cookie": f"espn_s2={self.AuthToken}"}

        params: dict = {"b": bracket, **PARAMS_BRACKET_CREATE}
        if entryId is not None:
            params["entryID"] = entryId

        url: str = URL_TOURNAMENT_CHALLENGE + URL_ENDPOINT_BRACKET_CREATE

        try:
            response: requests.Response = safe_requests.get(url, headers=headers, params=params)
            if response.status_code != 200:
                raise BracketSubmissionException(f"Status Code = {response.status_code}")

            entryIdMatch = re.search(fr"{URL_TOURNAMENT_CHALLENGE + URL_ENDPOINT_BRACKET_ENTRY}", response.text)
            if entryIdMatch is not None:
                entryIdNew: int = int(entryIdMatch.group(1))
                if entryId is not None and entryId != entryIdNew:
                    raise EntryIdMismatchException(f"{entryId} vs. {entryIdNew}")

                return entryIdNew

            raise BracketSubmissionException("Failed to Find EntryId")
        except Exception:
            raise BracketSubmissionException("Unknown Exception")
