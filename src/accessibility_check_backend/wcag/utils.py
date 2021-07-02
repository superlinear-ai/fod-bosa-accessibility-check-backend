"""Handy functions used in general."""

import uuid

import requests
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver


def render_url(url: str, window_width: int, window_height: int, scale: int) -> WebDriver:
    """Render the given URL in a web browser.

    Parameters
    ----------
    url : str
        The URL of the web page to render
    window_width : int
        The window width the web driver should have
    window_height : int
        The window height the web driver should have
    scale : int
        The scale factor the web driver should have

    Returns
    -------
    WebDriver
        The web driver containing the rendered web page
    """
    chrome_options = webdriver.chrome.options.Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument(f"--window-size={window_width}x{window_height}")
    chrome_options.add_argument(f"--force-device-scale-factor={scale}")
    chrome_options.add_argument("--no-sandbox")  # TODO: check whether we can remove this
    chrome_options.add_argument("--disable-dev-shm-usage")  # TODO: check whether we can remove this

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    return driver


def translate(text: str) -> str:
    """
    Translate the given text to English using Azure translate. Language detection is automatic.

    Parameters
    ----------
    text : str
        The text to translate

    Returns
    -------
    str
        The translation of the text.
    """
    # Azure translation settings
    subscription_key = "29e2d26befff4ebdbbb4ae339873a257"
    endpoint = "https://api.cognitive.microsofttranslator.com"
    location = "westeurope"

    path = "/translate"
    constructed_url = endpoint + path

    params = {"api-version": "3.0", "to": "en"}
    constructed_url = endpoint + path

    headers = {
        "Ocp-Apim-Subscription-Key": subscription_key,
        "Ocp-Apim-Subscription-Region": location,
        "Content-type": "application/json",
        "X-ClientTraceId": str(uuid.uuid4()),
    }

    body = [{"text": text}]

    request = requests.post(constructed_url, params=params, headers=headers, json=body)
    response = request.json()
    return str(response[0]["translations"][0]["text"])
