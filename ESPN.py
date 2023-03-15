from exceptions.BracketSubmissionException import BracketSubmissionException
from exceptions.EmailTakenException import EmailTakenException
from exceptions.EntryIdMismatchException import EntryIdMismatchException
from exceptions.InvalidEmailException import InvalidEmailException
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
import re
import requests
import time


ELEMENT_IFRAME = "//iframe[@name='oneid-iframe']"
ELEMENT_INPUT_BUTTON_SIGNUP = "//button[@id='BtnCreateAccount']"
ELEMENT_INPUT_BUTTON_SUBMIT = "//button[@id='BtnSubmit']"
ELEMENT_INPUT_TEXT_CODE = "//input[@id='InputRedeemOTP']"
ELEMENT_INPUT_TEXT_EMAIL = "//input[@type='email']"
ELEMENT_INPUT_TEXT_NAME_FIRST = "//input[@id='InputFirstName']"
ELEMENT_INPUT_TEXT_NAME_LAST = "//input[@id='InputLastName']"
ELEMENT_INPUT_TEXT_PASSWORD = "//input[@type='password']"

INPUT_NAME_FIRST = "Alec"
INPUT_NAME_LAST = "Masterson"

PARAMS_BRACKET_CREATE = {"r": "entry", "t1": 72, "t2": 65}

URL_ENDPOINT_BRACKET_CREATE = "/createOrUpdateEntry"
URL_ENDPOINT_BRACKET_ENTRY = "/entry\?entryID=(\d+)"

URL_LOGIN = "https://www.espn.com/login"
URL_TOURNAMENT_CHALLENGE = "https://fantasy.espn.com/tournament-challenge-bracket/2023/en"
URL_VALIDATE_EMAIL = "https://registerdisney.go.com/jgc/v8/client/ESPN-ONESITE.WEB-PROD/validate"

class ESPN:


    AuthToken: str
    Email: str
    __Driver: WebDriver
    __DriverWait: WebDriverWait


    def __init__(self, email: str):
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
        self.__Driver.get(URL_LOGIN)
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
            LOGGER.warning(f"{self.Email}: Code Required for Login")

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
        self.__DriverWait.until(EC.url_changes(URL_LOGIN))
        time.sleep(1)

        # Update the AuthToken for this ESPN account to allow API interactions.
        self.AuthToken = self.__Driver.get_cookie("espn_s2")["value"]


    def register(self) -> None:
        """
        Register/Sign-Up the email address with ESPN to create a new account.
        """
        self.validate_email()

        self.__Driver.get(URL_LOGIN)
        time.sleep(1)

        # Change the context of the WebDriver to the iFrame containing the registration form.
        elementIFrame: WebElement = self.get_element(ELEMENT_IFRAME, isInput=False)
        self.__Driver.switch_to.frame(elementIFrame)

        # Choose the "Sign Up" option, instead of logging in with an existing email address.
        self.get_element(ELEMENT_INPUT_BUTTON_SIGNUP).click()
        self.__DriverWait.until(EC.presence_of_element_located((By.XPATH, ELEMENT_INPUT_TEXT_NAME_FIRST)))
        time.sleep(1)

        # Enter the registration form data for the new account.
        self.get_element(ELEMENT_INPUT_TEXT_EMAIL).send_keys(self.Email)
        self.get_element(ELEMENT_INPUT_TEXT_NAME_FIRST).send_keys(INPUT_NAME_FIRST)
        self.get_element(ELEMENT_INPUT_TEXT_NAME_LAST).send_keys(INPUT_NAME_LAST)
        self.get_element(ELEMENT_INPUT_TEXT_PASSWORD).send_keys(INPUT_PASSWORD)
        time.sleep(1)

        # Submit the registration form and wait for the page to change to give confirmation.
        self.get_element(ELEMENT_INPUT_BUTTON_SUBMIT).submit()
        self.__DriverWait.until(EC.url_changes(URL_LOGIN))
        time.sleep(1)


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
            response: requests.Response = requests.get(url, headers=headers, params=params)
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


    def validate_email(self) -> None:
        response = requests.post(URL_VALIDATE_EMAIL, json = {"email": self.Email})
        if response.status_code == 200:
            return

        if "ACCOUNT_FOUND" in response.text:
            raise EmailTakenException

        raise InvalidEmailException
