"""Handy functions used in general."""

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
