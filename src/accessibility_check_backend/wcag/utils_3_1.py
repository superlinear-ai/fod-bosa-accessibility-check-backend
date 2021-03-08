"""Handy functions used by WCAG 3.1.1 and 3.1.2."""

import re
from typing import Optional

import langdetect
import lxml.html
import lxml.html.clean
from langdetect import DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
from selenium.webdriver.chrome.webdriver import WebDriver

DetectorFactory.seed = 0


def get_html_language(driver: WebDriver) -> Optional[str]:
    """Retrieve the web page's language as defined in its root element.

    The web page's language is defined in the page's html element: `<html lang='??-??'>`. Only the
    first two characters are returned by this function.

    Parameters
    ----------
    driver : WebDriver
        The web driver that contains the web page

    Returns
    -------
    Optional[str]
        The lang attribute of the web page's root element (if it is defined)
    """
    html_language: str = driver.execute_script("return document.documentElement.lang")
    if len(html_language) < 2:
        return None  # No lang attribute defined
    return html_language[:2]


def parse_page(driver: WebDriver) -> lxml.html.HtmlElement:
    """Parse the given web page into an `lxml` HTML element.

    Note: Only the body of the web page is returned (after cleaning).

    Parameters
    ----------
    driver : WebDriver
        The Selenium driver containing the web page to parse

    Returns
    -------
    lxml.html.HtmlElement
        An `lxml` HTML element containing the body of the web page
    """
    # Scroll to the bottom of the page
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Parse the page's body using lxml and creates a correct html document
    raw_html = lxml.html.document_fromstring(driver.page_source)

    # Clean the html
    cleaner = lxml.html.clean.Cleaner(
        page_structure=False,
        frames=False,
        forms=False,
        annoying_tags=False,
        safe_attrs=lxml.html.defs.safe_attrs | {"aria-label"},
        remove_unknown_tags=False,
    )
    cleaner(raw_html)

    # Obtain the body
    body_html = raw_html.find("body")

    # Scroll back to the top of the page
    driver.execute_script("window.scrollTo(0, 0);")
    return body_html


def count_words(text: str) -> int:
    """Count the number of words in the text.

    Parameters
    ----------
    text : str
        The text to count the number of words in

    Returns
    -------
    int
        The number of words
    """
    return len(re.findall(r"\b[^\d\W]+\b", text))


def predict_language(text: str) -> Optional[str]:
    """Predict the language of the given text.

    Parameters
    ----------
    text : str
        The text to predict the language of

    Returns
    -------
    Optional[str]
        The predicted language
    """
    try:
        detected_language: str = langdetect.detect(text)
    except LangDetectException:
        return None

    if detected_language in {"nl", "af"}:
        return "nl"
    elif detected_language in {"fr", "de", "en"}:
        return detected_language
    else:
        return None
