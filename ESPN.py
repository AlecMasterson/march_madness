from exceptions.BracketSubmissionException import BracketSubmissionException
from exceptions.EmailAvailabilityException import EmailAvailabilityException
from exceptions.EmailTakenException import EmailTakenException
from exceptions.EntryIdMismatchException import EntryIdMismatchException
from exceptions.InvalidEmailException import InvalidEmailException
from exceptions.RegistrationException import RegistrationException
from GMail import get_two_factor_code
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from typing import List
from util import build_submission_payload
from utils import LOGGER
import os
import requests
import time


ELEMENT_IFRAME = "//iframe[@name='disneyid-iframe']"
ELEMENT_INPUT_BUTTON_SIGNUP = "//button[@id='BtnCreateAccount']"
ELEMENT_INPUT_BUTTON_SUBMIT = "//button[@type='submit']"
ELEMENT_INPUT_TEXT_CODE = "//input[@placeholder='Code']"
ELEMENT_INPUT_TEXT_EMAIL = "//input[@type='email']"
ELEMENT_INPUT_TEXT_PASSWORD = "//input[@type='password']"


class ESPN:

    AuthToken: str
    Email: str
    Id: str

    __Driver: WebDriver
    __DriverWait: WebDriverWait

    __CONFIG = {}

    __ENDPOINT_BRACKET_CREATE = "/apis/v1/challenges/240/entries?platform=chui&view=chui_default"
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
    __URL_LOGIN = "https://espn.com/login"
    __URL_TOURNAMENT_CHALLENGE = "https://gambit-api.fantasy.espn.com"


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

        self.Email = f"{self.__CONFIG['EMAIL']}+{email}@gmail.com"
        self.Id = email


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

        Returns
        -------
        WebDriver
            A Selenium WebDriver instance to navigate ESPN.
        """
        driver_options: Options = Options()
        # driver_options.add_argument("--disable-dev-shm-usage")
        driver_options.add_argument("--headless")
        driver_options.add_argument("--incognito")
        driver_options.add_argument("--log-level=3")
        # driver_options.add_argument('--no-sandbox')

        return webdriver.Chrome(options=driver_options)


    # TODO: Review
    def check_availability(self) -> None:
        payload: dict = {"email": self.Email}
        url: str = self.__URL + self.__ENDPOINT_EMAIL_AVAILABILITY

        response: requests.Response = requests.post(url, json=payload)
        if not response.ok or response.status_code != 200:
            if "ACCOUNT_FOUND" in response.text:
                raise EmailTakenException

            raise EmailAvailabilityException(response.text)


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
        Login to ESPN to obtain the AuthToken for API interacion.
        """
        self.__Driver.get(self.__URL_LOGIN)
        time.sleep(1)

         # Change the context of the WebDriver to the iFrame containing the login form.
        elementIFrame: WebElement = self.get_element(ELEMENT_IFRAME, isInput=False)
        self.__Driver.switch_to.frame(elementIFrame)

        # Enter the login form data for the account.
        self.get_element(ELEMENT_INPUT_TEXT_EMAIL).send_keys(self.Email)
        self.get_element(ELEMENT_INPUT_TEXT_PASSWORD).send_keys(self.__CONFIG["PASSWORD"])
        time.sleep(1)

        # Submit the login form.
        self.get_element(ELEMENT_INPUT_BUTTON_SUBMIT).click()

        try:
            # Wait to see if an additional code is required for login.
            # If not required, this will quietly throw a TimeoutException.
            self.__DriverWait.until(EC.presence_of_element_located((By.XPATH, ELEMENT_INPUT_TEXT_CODE)))
            LOGGER.warning(f"{self.Email}: Code Required for Login")

            # Retrieve the code from GMail and enter the form data.
            self.get_element(ELEMENT_INPUT_TEXT_CODE).send_keys(get_two_factor_code(self.Email))
            time.sleep(1)

            # Submit the login form.
            self.get_element(ELEMENT_INPUT_BUTTON_SUBMIT).click()
        except TimeoutException:
            pass
        except Exception as e:
            LOGGER.error(f"{self.Email}: Failed to Provide Code, {e}")
            pass

        # Wait for the page to change to give confirmation of successful login.
        self.__DriverWait.until(EC.url_changes(self.__URL_LOGIN))

        # Update the AuthToken for this ESPN account to allow API interactions.
        # Previous wait condition is iffy, attempt to read cookie up to 5 times.
        attempt = 0
        while self.AuthToken is None and attempt < 5:
            try:
                time.sleep(1)
                self.AuthToken = self.__Driver.get_cookie("espn_s2")["value"]
            except:
                attempt += 1

        if self.AuthToken is None:
            raise Exception(f"{self.EMail}: Failed to Login")


    # TODO: Review
    def register(self) -> None:
        self.check_availability()

        payload: dict = self.__PAYLOAD_REGISTER.copy()
        payload["displayName"] = {"proposedDisplayName": self.__CONFIG["USERNAME"] + self.Id}
        payload["profile"]["email"] = self.Email
        payload["profile"]["username"] = self.__CONFIG["USERNAME"] + self.Id

        url: str = self.__URL + self.__ENDPOINT_REGISTER

        response: requests.Response = requests.post(url, json=payload, headers=self.__HEADERS, params=self.__PARAMS_REGISTER)
        if not response.ok or response.status_code != 200:
            raise RegistrationException(response.text)


    def submit(self, bracket: str) -> str:
        """
        Submit a bracket to ESPN and return the unique Id (generated by ESPN).

        Parameters
        ----------
        bracket : str

        Returns
        -------
        str - Unique Id (generated by ESPN) for the submitted bracket.

        Raises
        ------
        BracketSubmissionException
        """
        headers: dict = {
            "Content-Type": "application/json",
            "Cookie": f"espn_s2={self.AuthToken}"
        }
        params: dict = {
            "platform": "chui",
            "view": "chui_default"
        }
        payload: dict = build_submission_payload(bracket)
        url: str = "https://gambit-api.fantasy.espn.com/apis/v1/challenges/240/entries"

        response: requests.Response = requests.post(url, data=json.dumps(payload), headers=headers, params=params)
        if not response.ok or response.status_code != 200:
            raise BracketSubmissionException(f"{self.Email}: Failed to Submit, {response.status_code} - {response.text}")

        return response.json()["id"]
