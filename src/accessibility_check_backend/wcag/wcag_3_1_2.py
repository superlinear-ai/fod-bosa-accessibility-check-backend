"""Detect infractions against WCAG 3.1.2."""

from typing import List, Optional, Tuple

from lxml.etree import _ElementTree
from lxml.html import HtmlElement

from .type_aliases import Infraction
from .utils_3_1 import count_words, predict_language

MIN_WORDS_DEFAULT = 5
MIN_WORDS_HIDDEN = 3
HIDDEN_ATTRIBUTES = {"aria-label", "alt", "value", "title"}


def detect_wcag_3_1_2_infractions(body_html: HtmlElement, html_language: str) -> List[Infraction]:
    """Detect WCAG 3.1.2 infractions in the given web page.

    Parameters
    ----------
    body_html : HtmlElement
        The body of the web page
    html_language : str
        The page's defined language

    Returns
    -------
    List[Infraction]
        The detected infractions against WCAG 3.1.2
    """
    # Obtain the infractions recursively
    tree = body_html.getroottree()
    _, _, _, infractions = _dfs(tree, body_html, html_language, [])

    return infractions


def _dfs(
    tree: _ElementTree, element: HtmlElement, parent_language: str, infractions: List[Infraction]
) -> Tuple[str, Optional[str], Optional[str], List[Infraction]]:
    """Check for infractions against WCAG 3.1.2 using a recursive DFS.

    Parameters
    ----------
    tree : _ElementTree
        The root element tree of the web page, used to calculate the xpath
    element : HtmlElement
        The current element to check for infractions
    parent_language : str
        The defined language of the current element's parent
    infractions : List[Infraction]
        The infractions found until now

    Returns
    -------
    Tuple[str, Optional[str], Optional[str], List[Infraction]]
        A tuple containing:
          - the explicitly defined language of the current element
          - the detected language of the current element
          - the text of the current element
          - the infractions found
    """
    # If the current element does not have a `lang` attribute, take the parent's language
    defined_language = element.get("lang", parent_language)

    # The text contained in this element (and in this element alone)
    text = (element.text or "").replace("\n", " ").strip()

    # Check for infractions against WCAG 3.1.2 in hidden attributes
    hidden_infraction = _check_hidden_attributes(tree, element, defined_language)
    if hidden_infraction is not None:
        infractions.append(hidden_infraction)

    # Check for infractions against WCAG 3.1.2 in the current element's children
    children = element.getchildren()
    if children:
        # Run this function on each of the children (= recursion)
        children_results = [_dfs(tree, child, defined_language, infractions) for child in children]

        # Differ between children that are similar and children that are different
        if len({(defined, detected) for defined, detected, _, _ in children_results}) == 1:
            # All children have the same language defined and detected
            child_defined_language, child_detected_language, _, _ = children_results[0]
            if child_detected_language and child_defined_language != child_detected_language:
                # All children are wrong
                # Give a warning for the current element instead of for each of its children
                infractions.append(
                    {
                        "wcag_criterion": "WCAG_3_1_2",
                        "xpath": tree.getpath(element),
                        "html_language": child_defined_language,
                        "predicted_language": child_detected_language,
                    }
                )
        else:
            # The children have different values for their defined and detected languages
            for child, child_result in zip(children, children_results):
                child_defined_language, child_detected_language, _, _ = child_result
                if child_detected_language and child_detected_language != child_defined_language:
                    # This child is wrong, give a warning for only this child
                    infractions.append(
                        {
                            "wcag_criterion": "WCAG_3_1_2",
                            "xpath": tree.getpath(child),
                            "html_language": child_defined_language,
                            "predicted_language": child_detected_language,
                        }
                    )

        # If any of the children of the current element contains a very short piece of text, add it
        # to the current element's text
        for _, _, child_text, _ in children_results:
            # We only add the child text if it is short
            if child_text is not None and count_words(child_text) < MIN_WORDS_DEFAULT:
                text += " " + child_text

    # If the current element's text is long enough, predict its language
    if count_words(text) >= MIN_WORDS_DEFAULT:
        detected_language = predict_language(text)
    else:
        detected_language = None

    return defined_language, detected_language, text, infractions


def _check_hidden_attributes(
    tree: _ElementTree, element: HtmlElement, defined_language: str
) -> Optional[Infraction]:
    """Check for an infraction in the hidden attributes of an element.

    Parameters
    ----------
    tree : _ElementTree
        The root element tree of the web page, used to calculate the xpath
    element : HtmlElement
        The current element to check for an infraction
    defined_language : str
        The defined language of the current element

    Returns
    -------
    Optional[Infraction]
        Either an infraction against WCAG 3.1.2 or `None`
    """
    for attribute_name in HIDDEN_ATTRIBUTES:
        if attribute_name in element.attrib:
            attribute_value = element.attrib[attribute_name].strip()
            if count_words(attribute_value) < MIN_WORDS_HIDDEN:
                # If the hidden attribute's value is too short, we don't check its language
                continue
            detected_language = predict_language(attribute_value)
            if detected_language and defined_language != detected_language:
                # The hidden attribute is wrong, return an infraction
                return {
                    "wcag_criterion": "WCAG_3_1_2",
                    "xpath": tree.getpath(element),
                    "html_language": defined_language,
                    "predicted_language": detected_language,
                }
    return None
