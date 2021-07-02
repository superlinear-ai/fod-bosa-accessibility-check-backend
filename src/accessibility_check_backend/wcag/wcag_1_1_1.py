"""Detect infractions against WCAG 1.1.1."""
from typing import List

import requests
from PIL import Image
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from sentence_transformers import SentenceTransformer, util

from ..models import AltTextInfraction
from .utils import translate
from .utils_1_4 import get_xpath_of_element


def detect_wcag_1_1_1_infractions(driver: WebDriver) -> List[AltTextInfraction]:
    """Detect WCAG 1.1.1 infractions in the given web page.

    Parameters
    ----------
    driver : WebDriver
        The web driver that contains the web page

    Returns
    -------
    List[AltTextInfraction]
        The detected infractions against WCAG 1.1.1
    """
    # model = SentenceTransformer("/app/src/accessibility_check_backend/wcag/clip-ViT-B-32/")
    model = SentenceTransformer("clip-ViT-B-32")
    infractions = []

    for el in driver.find_elements(By.TAG_NAME, "img"):
        if not el.get_attribute("alt"):
            continue

        try:
            image = Image.open(requests.get(el.get_attribute("src"), stream=True).raw)
        except Exception as e:
            print(f"Exception: {e}")
            continue

        img_emb = model.encode(image)  # Embed image
        orig_text = el.get_attribute("alt")
        text = translate(orig_text)
        text_emb = model.encode(text)  # Embed text
        cosine_score = util.pytorch_cos_sim(
            img_emb, text_emb
        ).item()  # Compute cosine between image and text embeddings

        # print(f"{orig_text}, {text}, {cosine_score}")

        type = 1 if cosine_score < 0.18 else 2

        if cosine_score < 0.21:
            infractions.append(
                AltTextInfraction(
                    wcag_criterion="WCAG_1_1_1",
                    xpath=get_xpath_of_element(el),
                    text=el.get_attribute("alt"),
                    type=type,
                )
            )

    return infractions
