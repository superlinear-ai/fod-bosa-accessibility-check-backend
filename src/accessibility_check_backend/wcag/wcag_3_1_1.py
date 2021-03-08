"""Detect infractions against WCAG 3.1.1."""

from collections import deque
from typing import List

from lxml.html import HtmlElement

from .type_aliases import Infraction
from .utils_3_1 import count_words, predict_language

MIN_WORDS_DEFAULT = 5


def detect_wcag_3_1_1_infractions(body_html: HtmlElement, html_language: str) -> List[Infraction]:
    """Detect WCAG 3.1.1 infractions in the given web page.

    Parameters
    ----------
    body_html : HtmlElement
        The body of the web page
    html_language : str
        The page's defined language

    Returns
    -------
    List[Infraction]
        The detected infractions against WCAG 3.1.1
    """
    # Get the page's contents
    root_text = _get_root_text(body_html)
    if count_words(root_text) < MIN_WORDS_DEFAULT:
        return []  # not enough words to accurately predict the language

    # Predict the language of the root text
    predicted_language = predict_language(root_text)

    # Check whether the page's defined language is the same as its predicted language
    if predicted_language and predicted_language != html_language:
        return [
            {
                "wcag_criterion": "WCAG_3_1_1",
                "xpath": "/html",
                "html_language": html_language,
                "predicted_language": predicted_language,
            }
        ]
    else:
        return []


def _get_root_text(body_html: HtmlElement) -> str:
    """Retrieve the root text of the given web page.

    Note: Root text means that any element that has a `lang` attribute is ignored, along with its
    children.

    This function traverses the web page using iterative depth-first search.


    Parameters
    ----------
    body_html : HtmlElement
        The body of the given web page

    Returns
    -------
    str
        The root text of the given web page
    """
    stack = deque([body_html])
    text_parts = []
    while stack:
        element = stack.popleft()
        if element.get("lang", None):
            continue  # This element and its children are ignored as it has a `lang` attribute
        stack.extend(element.getchildren())
        if element.text and (text := element.text.strip()):
            text_parts.append(text)
    return " ".join(text_parts)
