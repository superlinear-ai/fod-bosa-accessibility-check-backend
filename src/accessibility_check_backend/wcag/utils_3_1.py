"""Handy functions used by WCAG 3.1.1 and 3.1.2."""

import re
from functools import lru_cache
from typing import Optional

import lxml.html
import lxml.html.clean
from langid.langid import LanguageIdentifier, model
from selenium.webdriver.chrome.webdriver import WebDriver

URL_REGEX = re.compile(r"(https?://|www)[-_.?&~;+=/#0-9A-Za-z]{1,2076}")
EMAIL_REGEX = re.compile(r"[-_.0-9A-Za-z]{1,64}@[-_0-9A-Za-z]{1,255}[-_.0-9A-Za-z]{1,255}")
WORD_REGEX = re.compile(r"\b[^\d\W]+\b")
LANGUAGES = ["nl", "fr", "de", "en"]
MIN_LANGUAGE_PROBABILITY = 0.8


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


def clean_text(text: str) -> str:
    """Clean the given text.

    Removes URLs, email addresses and only keeps words.

    Parameters
    ----------
    text : str
        The text to clean

    Returns
    -------
    str
        The cleaned text
    """
    text = URL_REGEX.sub("", text)  # remove URLs
    text = EMAIL_REGEX.sub("", text)  # remove email addresses
    text = " ".join(WORD_REGEX.findall(text))  # only keep words
    return text


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
    return len(clean_text(text).split())


@lru_cache(maxsize=1)
def _get_language_identifier() -> LanguageIdentifier:
    # Make sure that the probabilities are normalized
    # https://github.com/saffsd/langid.py#probability-normalization
    language_identifier = LanguageIdentifier.from_modelstring(model, norm_probs=True)
    language_identifier.set_languages(LANGUAGES)
    return language_identifier


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
    language: str
    language, probability = _get_language_identifier().classify(clean_text(text))
    if probability > MIN_LANGUAGE_PROBABILITY:
        return language
    else:
        return None
