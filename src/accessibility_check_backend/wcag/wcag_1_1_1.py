"""Detect infractions against WCAG 1.1.1."""
from io import BytesIO
from typing import List

import cairosvg
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
    More specifically, detect images which do not seem to match their alt text.

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

    ERROR_THRESHOLD = 0.25
    WARNING_THRESHOLD = 0.27

    for el in driver.find_elements(By.TAG_NAME, "img"):
        if not el.get_attribute("alt"):
            continue

        src = el.get_attribute("src")
        ext = src[-3:]

        try:
            if ext == "svg":
                out = BytesIO()
                cairosvg.svg2png(url=src, write_to=out)
                image = Image.open(out)
            else:
                image = Image.open(requests.get(src, stream=True).raw).convert("RGB")
        except Exception as e:
            print(f"Exception: {e} for url {src}")
            continue

        print(image)

        try:
            img_emb = model.encode(image)  # Embed image
        except Exception as e:
            continue

        # orig_text = el.get_attribute("alt")
        # text = translate(orig_text)
        # text_emb = model.encode(text)  # Embed text
        # cosine_score = util.pytorch_cos_sim(
        #     img_emb, text_emb
        # ).item()  # Compute cosine between image and text embeddings

        # print(f"{orig_text}, {text}, {cosine_score}")

        # # type = 1 if cosine_score < ERROR_THRESHOLD else 2

        # if cosine_score < WARNING_THRESHOLD:
        #     infractions.append(
        #         AltTextInfraction(
        #             wcag_criterion="WCAG_1_1_1",
        #             xpath=get_xpath_of_element(el),
        #             text=el.get_attribute("alt"),
        #             type=2,  # 1 = error, 2 = warning ; we decided that all 1.1.1 errors should be warnings
        #         )
        #     )

    return infractions
