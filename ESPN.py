from exceptions.BracketSubmissionException import BracketSubmissionException
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.service import Service
from exceptions.EmailAvailabilityException import EmailAvailabilityException
from exceptions.EmailTakenException import EmailTakenException
from Gmail import Gmail
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from typing import List, Optional
from util import build_submission_payload
from utils import LOGGER
import json
import os
import requests
import time
import secrets


ELEMENT_IFRAME = "//iframe[@name='disneyid-iframe']"
ELEMENT_IFRAME_SIGNUP = "//iframe[@name='oneid-iframe']"
ELEMENT_INPUT_BUTTON_SUBMIT = "//button[@type='submit']"
ELEMENT_INPUT_TEXT_CODE = "//input[@placeholder='Code']"
ELEMENT_INPUT_TEXT_EMAIL = "//input[@type='email']"
ELEMENT_INPUT_TEXT_NAME_FIRST = "//input[@placeholder='First Name']"
ELEMENT_INPUT_TEXT_NAME_LAST = "//input[@placeholder='Last Name']"
ELEMENT_INPUT_TEXT_PASSWORD = "//input[@type='password']"

ELEMENT_LINK_SIGNUP = "//a[@tref='/members/v3_1/login' and text()='Sign Up' and not(ancestor::div[@id='header-wrapper'])]"
ELEMENT_LINK_USER = "//a[@id='global-user-trigger']"


class ESPN:

    AuthToken: Optional[str]
    Email: str

    __Driver: WebDriver
    __DriverWait: WebDriverWait

    __CONFIG = {
        "NAME_FIRST": "Alec",
        "NAME_LAST": "Masterson",
        "PASSWORD": "Madness01"
    }

    __URL = "https://espn.com"
    __URL_LOGIN = "https://espn.com/login"


    def __init__(self, email: str):
        try:
            pass
        except:
            raise Exception("Environment Variables Missing, Please Check Requirements in README")

        self.AuthToken = None
        self.Email = email


    def __enter__(self):
        self.__Driver = self.__create_driver()
        self.__DriverWait = WebDriverWait(self.__Driver, timeout=20)

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
        driver_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
        driver_options.add_argument('--no-sandbox')

        # return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=driver_options)
        return webdriver.Chrome(options=driver_options)


    def check_availability(self) -> None:
        headers: dict = {
            "Content-Type": "application/json"
        }
        payload: dict = {
            "email": self.Email
        }
        url: str = "https://registerdisney.go.com/jgc/v8/client/ESPN-ONESITE.WEB-PROD/validate"

        response: requests.Response = requests.post(url, data=json.dumps(payload), headers=headers)
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
        LOGGER.info(f"{self.Email}: Attempting to Login")

        try:
            self.check_availability()
            self.register()
            return
        except EmailTakenException:
            pass

        self.__Driver.get(self.__URL_LOGIN)
        self.__wait()

         # Change the context of the WebDriver to the iFrame containing the login form.
        elementIFrame: WebElement = self.get_element(ELEMENT_IFRAME, isInput=False)
        self.__Driver.switch_to.frame(elementIFrame)

        # Enter the login form data for the account.
        self.get_element(ELEMENT_INPUT_TEXT_EMAIL).send_keys(self.Email)
        self.get_element(ELEMENT_INPUT_TEXT_PASSWORD).send_keys(self.__CONFIG["PASSWORD"])
        self.__wait()

        # Submit the login form.
        self.get_element(ELEMENT_INPUT_BUTTON_SUBMIT).click()

        self.__submit_gmail_code()
        self.__get_token()


    def test_register(self) -> None:
        payload: dict = {
            "profile": {
                "email": "masterson.march.madness+718@gmail.com",
                "verifyEmail": "masterson.march.madness+718@gmail.com",
                "firstName": "Alec",
                "lastName": "Masterson",
                "region": "US"
            },
            "legalAssertions": [
                "gtou_ppv2_proxy"
            ],
            "password": "Madness01"
        }
        url: str = "https://registerdisney.go.com/jgc/v8/client/ESPN-ONESITE.WEB-PROD/guest/register?autogeneratePassword=false&autogenerateUsername=true&feature=no-password-reuse&langPref=en-US"

        script = f"""
        const fetchData = async () => {{
          const response = await fetch('{url}', {{method: 'POST', mode: 'no-cors', headers: {{'Authorization': 'APIKEY Ay3eiewEnwddn76lBwMDQwfZ7/LUNeVN+vqYQtvm6BFvglAxz63fTABrwHw4ErfubFI+lQ93HdERR6oAS29o1U1FTJWv', 'Content-Type': 'application/json'}}, body: JSON.stringify({payload})}}).then(response => response.json());
          const data = await response.json();
          return data;
        }};

        fetchData().then(data => {{
          console.log(data);
          arguments[arguments.length - 1](data);
        }}).catch(error => {{
          console.error(error);
          arguments[arguments.length - 1](null);
        }})
        """
        response = self.__Driver.execute_async_script(script)
        print(response)
        # Retrieve console log messages
        logs = self.__Driver.get_log("browser")

        # Print console log messages
        for log in logs:
            print(log['message'])


    def register(self) -> None:
        """
        Register with ESPN to obtain the AuthToken for API interacion.
        """
        LOGGER.info(f"{self.Email}: Attempting to Register")
        self.__Driver.get(self.__URL)
        self.__wait()

        self.__DriverWait.until(EC.presence_of_element_located((By.XPATH, ELEMENT_LINK_USER)))
        self.__DriverWait.until(EC.visibility_of_element_located((By.XPATH, ELEMENT_LINK_USER)))
        self.__DriverWait.until(EC.element_to_be_clickable((By.XPATH, ELEMENT_LINK_USER)))
        self.__save_screenshot("register-1")
        self.get_element(ELEMENT_LINK_USER, isInput=False).click()
        self.__wait()

        self.__DriverWait.until(EC.presence_of_element_located((By.XPATH, ELEMENT_LINK_SIGNUP)))
        self.__DriverWait.until(EC.element_to_be_clickable((By.XPATH, ELEMENT_LINK_SIGNUP)))
        self.__save_screenshot("register-2")
        self.get_element(ELEMENT_LINK_SIGNUP, isInput=False).click()
        self.__wait()

        self.__DriverWait.until(EC.presence_of_element_located((By.XPATH, ELEMENT_IFRAME_SIGNUP)))
        self.__Driver.switch_to.frame(self.get_element(ELEMENT_IFRAME_SIGNUP, isInput=False))
        self.__DriverWait.until(EC.presence_of_element_located((By.XPATH, ELEMENT_INPUT_TEXT_EMAIL)))
        self.__save_screenshot("register-3")
        self.get_element(ELEMENT_INPUT_TEXT_EMAIL).send_keys(self.Email)
        self.__wait()

        self.__save_screenshot("register-4")
        self.get_element(ELEMENT_INPUT_BUTTON_SUBMIT).click()
        self.__wait()

        self.__DriverWait.until(EC.presence_of_element_located((By.XPATH, ELEMENT_INPUT_TEXT_NAME_FIRST)))
        self.__save_screenshot("register-5")
        self.get_element(ELEMENT_INPUT_TEXT_NAME_FIRST).send_keys(self.__CONFIG["NAME_FIRST"])
        self.get_element(ELEMENT_INPUT_TEXT_NAME_LAST).send_keys(self.__CONFIG["NAME_LAST"])
        self.get_element(ELEMENT_INPUT_TEXT_PASSWORD).send_keys(self.__CONFIG["PASSWORD"])
        self.__wait()

        self.__save_screenshot("register-6")
        self.get_element(ELEMENT_INPUT_BUTTON_SUBMIT).click()
        self.__wait()

        self.__submit_gmail_code()
        self.__get_token()


    def __get_token(self) -> None:
        start: float = time.time()
        while time.time() - start < 10:
            try:
                self.__save_screenshot(f"token-{time.time()}")
                self.AuthToken = self.__Driver.get_cookie("espn_s2")["value"]
                LOGGER.info(f"{self.Email}: Successfully Got Token")
                return
            except:
                self.__wait()

        """
        logs = []
        raw = []
        for entry in self.__Driver.get_log("performance"):
            raw.append(entry)
            logs.append(json.loads(entry["message"]))

        with open("test.txt", "w") as file:
            file.write(str(raw))
            file.close()
        with open("test.json", "w") as file:
            file.write(json.dumps(logs))
            file.close()
        """

        self.__save_screenshot("token-fail")
        raise Exception(f"{self.Email}: Failed to Get Token")


    def __save_screenshot(self, name: str) -> None:
        path: str = f"./data/screenshots/{self.Email}"

        if not os.path.exists(path):
            os.makedirs(path)

        self.__Driver.save_screenshot(f"{path}/{name}.png")


    def __submit_gmail_code(self) -> None:
        try:
            # Wait to see if an additional code is required for login.
            # If not required, this will quietly throw a TimeoutException.
            # self.__Driver.maximize_window()
            # self.__Driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            self.__save_screenshot("code-1")
            LOGGER.warning(f"{self.Email}: Waiting to See if Code is Required")
            self.__wait()

            self.__save_screenshot("code-2")
            self.__DriverWait.until(EC.presence_of_element_located((By.XPATH, ELEMENT_INPUT_TEXT_CODE)))
            self.__save_screenshot("code-3")
            LOGGER.warning(f"{self.Email}: Code Required")

            # Retrieve the code from GMail and enter the form data.
            with Gmail() as gmail:
                code: str = gmail.get_code(self.Email)
                LOGGER.info(f"{self.Email}: Successfully Got Code, Code='{code}'")

                self.get_element(ELEMENT_INPUT_TEXT_CODE).send_keys(code)
                self.__save_screenshot("code-4")
                self.__wait()

            self.get_element(ELEMENT_INPUT_BUTTON_SUBMIT).click()
        except TimeoutException:
            LOGGER.warning(f"{self.Email}: Timeout while Waiting to See if Code is Required")
            pass

    def __wait(self) -> None:
        time.sleep(secrets.SystemRandom().uniform(-0.5, 0.5) + secrets.SystemRandom().uniform(1, 4))


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

        id: str = response.json()["id"]
        LOGGER.info(f"{self.Email}: Successfully Submitted Bracket, Id='{id}', Bracket='{bracket}'")

        return id


def submit_bracket(email: str, token: str, bracket: str) -> str:
    headers: dict = {
        "Content-Type": "application/json",
        "Cookie": f"espn_s2={token}"
    }
    params: dict = {
        "platform": "chui",
        "view": "chui_default"
    }
    payload: dict = build_submission_payload(bracket)
    url: str = "https://gambit-api.fantasy.espn.com/apis/v1/challenges/240/entries"

    response: requests.Response = requests.post(url, data=json.dumps(payload), headers=headers, params=params)
    if not response.ok or response.status_code != 200:
        raise BracketSubmissionException(f"{email}: Failed to Submit, {response.status_code} - {response.text}")

    id: str = response.json()["id"]
    LOGGER.info(f"{email}: Successfully Submitted Bracket, Id='{id}', Bracket='{bracket}'")

    return id


if __name__ == "__main__":
    for i in range(689, 690):
        with ESPN(f"masterson.march.madness+{i}@gmail.com") as espn:
            espn.login()
            # print(f"{i}: {espn.AuthToken}")
# masterson.march.madness+647@gmail.com
