"""Detect infractions against WCAG 1.4.11."""

from typing import List, Optional

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from ..models import ContrastInfraction
from .type_aliases import Image
from .utils_1_4 import get_contrast_ratio, get_xpath_of_element

MIN_CONTRAST_RATIO = 3.0


def detect_wcag_1_4_11_infractions(driver: WebDriver, img: Image) -> List[ContrastInfraction]:
    """Detect WCAG 1.4.11 infractions in the given web page.

    Parameters
    ----------
    driver : WebDriver
        The web driver that contains the web page
    img : Image
        A screenshot of the web page (taken by the given web driver)

    Returns
    -------
    List[ContrastInfraction]
        The detected infractions against WCAG 1.4.11
    """
    input_elements = find_input_elements(driver)
    infractions = []
    for element in input_elements:
        contrast_ratio = get_input_element_contrast_ratio(element, img)
        if contrast_ratio is not None and contrast_ratio < MIN_CONTRAST_RATIO:
            infractions.append(
                ContrastInfraction(
                    wcag_criterion="WCAG_1_4_11",
                    xpath=get_xpath_of_element(element),
                    contrast=contrast_ratio,
                    contrast_threshold=MIN_CONTRAST_RATIO,
                )
            )
    return infractions


def find_input_elements(driver: WebDriver) -> List[WebElement]:
    """Find the input elements in the given web page.

    Parameters
    ----------
    driver : WebDriver
        The web driver that contains the web page

    Returns
    -------
    List[WebElement]
        A list of DOM elements
    """
    # Define the xpaths for all possible input elements
    input_types = [
        "text",
        "password",
        "email",
        "search",
        "url",
        "number",
        "tel",
        "date",
        "time",
        "datetime-local",
        "month",
        "week",
        "range",
        "submit",
        "reset",
        "button",
        "file",
        "checkbox",
        "radio",
    ]
    input_xpaths = [f"//input[@type='{input_type}']" for input_type in input_types]
    other_xpaths = ["//button", "//option", "//textarea", "//datalists"]

    # Search for these xpaths in the given web page and return their DOM elements
    return driver.find_elements_by_xpath(" | ".join(input_xpaths + other_xpaths))  # type: ignore


def get_input_element_contrast_ratio(input_element: WebElement, img: Image) -> Optional[float]:
    """Get the contrast ratio of the given input element.

    Parameters
    ----------
    input_element : WebElement
        The DOM element fow which we need the contrast ratio
    img : Image
        A screenshot of the full web page where the element should be visible

    Returns
    -------
    Optional[float]
        The contrast ratio inside the given element (if the contrast ratio can be computed)
    """
    # Define the top-right point of the rectangle encompassing the element (with scale factor 2)
    x1, y1 = input_element.location["x"] * 2, input_element.location["y"] * 2

    # Define the width and height of the element (with scale factor 2)
    w, h = input_element.size["width"] * 2, input_element.size["height"] * 2

    # Define the bottom-left point of the rectangle encompassing the element
    x2, y2 = x1 + w, y1 + h

    # If the encompassing rectangle is 0 pixels wide or high, we can't compute anything
    if x1 == x2 or y1 == y2:
        return None

    # Crop the screenshot to the encompassing rectangle after enlarging it with `d` pixels
    d = 20
    element_img = img[y1 - d : y2 + d, x1 - d : x2 + d]

    # If the image is 0 pixels large, we can't compute anything
    if element_img.size == 0:
        return None

    # Compute the contrast ratio inside the cropped screenshot
    return get_contrast_ratio(element_img, d, w + d, d, h + d)
