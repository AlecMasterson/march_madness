from exceptions.EmailTakenException import EmailTakenException
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from typing import List, Union
import time


ELEMENT_ERROR = "input-error"
ELEMENT_FORM = "//form"
ELEMENT_IFRAME = "//iframe[@name='oneid-iframe']"
ELEMENT_INPUT_BUTTON_SIGNUP = "//button[@id='BtnCreateAccount']"
ELEMENT_INPUT_TEXT_EMAIL = "//input[@type='email']"
ELEMENT_INPUT_TEXT_NAME_FIRST = "//input[@id='InputFirstName']"
ELEMENT_INPUT_TEXT_NAME_LAST = "//input[@id='InputLastName']"
ELEMENT_INPUT_TEXT_PASSWORD = "//input[@type='password']"

INPUT_NAME_FIRST = "Alec"
INPUT_NAME_LAST = "Masterson"
INPUT_PASSWORD = ""

URL_LOGIN = "https://www.espn.com/login"


class ESPN:


    Email: str
    __Driver: WebDriver
    __DriverWait: WebDriverWait


    def __init__(self, email: str):
        self.Email = email


    def __enter__(self):
        self.__Driver = self.__create_driver()
        self.__DriverWait = WebDriverWait(self.__Driver, timeout=8)

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
        driver_options.add_argument("--headless")

        return webdriver.Chrome(options=driver_options)


    def get_element(self, xpath: str, isInput: bool = True) -> Union[NoSuchElementException, WebElement]:
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
        Union[NoSuchElementException, WebElement]
            The desired element, or a NoSuchElementException if the criteria is met.

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


    def register(self) -> None:
        """
        Register/Sign-Up the email address with ESPN to create a new account.
        """
        self.__Driver.get(URL_LOGIN)
        time.sleep(1)

        # Change the context of the WebDriver to the iFrame containing the registration form.
        elementIFrame: WebElement = self.get_element(ELEMENT_IFRAME, isInput=False)
        self.__Driver.switch_to.frame(elementIFrame)

        # Choose the "Sign Up" option, instead of logging in with an existing email address.
        self.get_element(ELEMENT_INPUT_BUTTON_SIGNUP).click()
        self.__DriverWait.until(EC.presence_of_element_located((By.XPATH, ELEMENT_INPUT_TEXT_EMAIL)))
        time.sleep(1)

        # Enter the registration form data for the new account.
        self.get_element(ELEMENT_INPUT_TEXT_EMAIL).send_keys(self.Email)
        self.get_element(ELEMENT_INPUT_TEXT_NAME_FIRST).send_keys(INPUT_NAME_FIRST)
        self.get_element(ELEMENT_INPUT_TEXT_NAME_LAST).send_keys(INPUT_NAME_LAST)
        self.get_element(ELEMENT_INPUT_TEXT_PASSWORD).send_keys(INPUT_PASSWORD)
        time.sleep(1)

        # Check for error message indicating that the email address has already been registered with ESPN.
        # All other potential error messages will be caught when the form submission is unsuccessful.
        errors: List[WebElement] = self.__Driver.find_elements(by=By.CLASS_NAME, value=ELEMENT_ERROR)
        for error in [error for error in errors if error.is_displayed()]:
            if "email has already been used" in error.get_attribute("innerHTML"):
                raise EmailTakenException

        # Submit the registration form and wait for the page to change to give confirmation.
        self.get_element(ELEMENT_FORM, isInput=False).submit()
        self.__DriverWait.until(EC.url_changes(URL_LOGIN))
