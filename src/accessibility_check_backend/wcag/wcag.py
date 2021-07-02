"""General file to detect WCAG infractions."""

from typing import List

from ..models import Infraction
from .utils import render_url
from .utils_1_4 import take_screenshot
from .utils_3_1 import get_html_language, parse_page
from .wcag_1_1_1 import detect_wcag_1_1_1_infractions
from .wcag_1_4_3 import detect_wcag_1_4_3_infractions
from .wcag_1_4_11 import detect_wcag_1_4_11_infractions
from .wcag_3_1_1 import detect_wcag_3_1_1_infractions
from .wcag_3_1_2 import detect_wcag_3_1_2_infractions


def detect_wcag_infractions(url: str, window_width: int, window_height: int) -> List[Infraction]:
    """Detect all WCAG infractions for the given URL.

    Parameters
    ----------
    url : str
        The URL of the web page we want to investigate
    window_width : int
        The window width of the browser we will simulate
    window_height : int
        The window height of the browser we will simulate

    Returns
    -------
    List[Infraction]
        The detected infractions against WCAG
    """
    infractions: List[Infraction] = []

    # Preparations
    driver_small = render_url(url, window_width, window_height, scale=1)
    img_small = take_screenshot(driver_small)
    driver_large = render_url(url, window_width, window_height, scale=2)
    img_large = take_screenshot(driver_large)
    body_html = parse_page(driver_small)
    html_language = get_html_language(driver_small)

    # Detect infractions against WCAG 1.4.3 and 1.4.11
    infractions += detect_wcag_1_4_3_infractions(driver_small, img_small, img_large)
    infractions += detect_wcag_1_4_11_infractions(driver_large, img_large)

    # # Detect infractions against WCAG 3.1.1 and 3.1.2
    if html_language:
        infractions += detect_wcag_3_1_1_infractions(body_html, html_language)
        infractions += detect_wcag_3_1_2_infractions(body_html, html_language)

    # Detect infractions against WCAG 3.1.1 and 3.1.2
    infractions += detect_wcag_1_1_1_infractions(driver_large)

    # Clean up
    driver_small.quit()
    driver_large.quit()

    # Return the list of infractions
    return infractions
