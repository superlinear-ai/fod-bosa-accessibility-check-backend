"""General file to detect WCAG infractions."""

import time
from pathlib import Path
from typing import List

import cv2

from .type_aliases import Infraction
from .utils import take_screenshot
from .wcag_1_4_3 import detect_wcag_1_4_3_infractions
from .wcag_1_4_11 import detect_wcag_1_4_11_infractions


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
    # Create the temp folder if it doesn't yet exist
    folder = Path("temp/")
    folder.mkdir(exist_ok=True)

    # Take a small and a large screenshot and keep the browser tabs (i.e. drivers) open
    t = int(time.time() * 1000)
    filename_small = folder / f"capture-{t}-small.png"
    driver_small = take_screenshot(url, window_width, window_height, filename_small, scale=1)
    img_small = cv2.imread(str(filename_small))
    filename_large = folder / f"capture-{t}-large.png"
    driver_large = take_screenshot(url, window_width, window_height, filename_large, scale=2)
    img_large = cv2.imread(str(filename_large))

    # Detect infractions against WCAG
    infractions = detect_wcag_1_4_3_infractions(driver_small, img_small, img_large)
    infractions += detect_wcag_1_4_11_infractions(driver_large, img_large)

    # Clean up
    filename_small.unlink()
    filename_large.unlink()
    driver_small.close()
    driver_large.close()

    # Return the list of infractions
    return infractions
