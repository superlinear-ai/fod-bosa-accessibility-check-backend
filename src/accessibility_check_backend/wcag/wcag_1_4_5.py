"""Detect WCAG 1.4.5 infractions."""
import re
import urllib
from functools import lru_cache
from io import BytesIO
from pathlib import Path
from typing import List

import cairosvg
import cv2
import numpy as np
import requests
from imutils.object_detection import non_max_suppression
from PIL import Image
from selenium.webdriver.chrome.webdriver import WebDriver
from sentence_transformers import SentenceTransformer, util

from ..models import AltTextInfraction
from .utils_1_4 import get_xpath_of_element


@lru_cache(maxsize=1)
def get_east_model() -> cv2.dnn_Net:
    """Retrieve the (cached) EAST model.

    Returns
    -------
    cv2.dnn_Net
        The EAST model
    """
    current_directory = Path(__file__).resolve().parent
    file_path = current_directory / "east_model" / "frozen_east_text_detection.pb"
    return cv2.dnn.readNet(str(file_path))


def find_decorative_and_nondecoratives(driver):
    """Separate decorative from non-decorative images.

    Parameters
    ----------
    driver : WebDriver
        The web driver that contains the web page   
    """

    def has_text(el):
        if el.get_attribute("textContent"):
            return True
        children = el.find_elements_by_xpath(".//*")
        return any([has_text(el) for el in children])

    def is_icon(el):
        #         return el.size['height'] == el.size['width'] and el.size['width'] <= 64
        return el.size["width"] <= 64 and el.size["height"] <= 64

    def contains_text(src):
        req = urllib.request.urlopen(src)
        arr = np.asarray(bytearray(req.read()), dtype=np.uint8)

        try:
            img = cv2.imdecode(arr, -1)
        except:
            return False

        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        surface, _ = EAST(img)
        ratio = surface / (img.shape[0] * img.shape[1])
        return surface and ratio > 0.7

    non_img_links = [
        el.get_attribute("href")
        for el in driver.find_elements_by_xpath("//a[not(descendant::img)]")
    ]

    block_link_images = []
    for el in driver.find_elements_by_xpath("//a[descendant::img]"):
        if has_text(el):
            block_link_images.append(el.find_elements_by_xpath(".//img")[0].get_attribute("src"))

    nondecorative = set()
    decorative = set()
    alts = {}
    els = {}
    # Check if link and not redundant with text link + size
    for el in driver.find_elements_by_xpath("//a//img"):
        src = el.get_attribute("src")
        alts[src] = el.get_attribute("alt")
        els[src] = el
        parent = el.find_element_by_xpath("..")
        url = parent.get_attribute("href")
        if not is_icon(el) and (url in non_img_links or src in block_link_images):
            decorative.add(src)
        else:
            nondecorative.add(src)

    # Iterates over non-link images not iterated over before
    for el in driver.find_elements_by_xpath("//img"):
        src = el.get_attribute("src")
        alts[src] = el.get_attribute("alt")
        els[src] = el
        if not (src in nondecorative) and not (src in decorative):
            decorative.add(src)

    have_text = set()

    for src in nondecorative:
        if contains_text(src):
            have_text.add(src)

    moves = []
    for src in decorative:
        if src is None or len(src) == 0:
            continue
        ext = re.findall(r".+\.([a-z]{3,4}).*", src)
        if len(ext) and ext[0] == "svg":
            continue
        if contains_text(src):
            have_text.add(src)
            moves.append(src)

    for src in moves:
        decorative.remove(src)
        nondecorative.add(src)

    return nondecorative, have_text, alts, els


def match_text(src, txt):
    model = SentenceTransformer("clip-ViT-B-32")

    ext = re.findall(r".+\.([a-z]{3,4}).*", src)
    if len(ext) == 0:
        return True

    ext = ext[0]
    if ext == "svg":
        out = BytesIO()
        cairosvg.svg2png(url=src, write_to=out)
        image = Image.open(out)
    else:
        image = Image.open(requests.get(src, stream=True).raw).convert("RGB")

    img_emb = model.encode(image)  # Embed image
    text_emb = model.encode(txt)  # Embed text
    cosine_score = util.pytorch_cos_sim(img_emb, text_emb).item()

    return cosine_score >= 0.24


def EAST(image):
    orig = image.copy()
    (H, W) = image.shape[:2]

    # set the new width and height and then determine the ratio in change
    # for both the width and height
    s = 320
    (newW, newH) = (s, s)
    rW = W / float(newW)
    rH = H / float(newH)

    # resize the image and grab the new image dimensions
    image = cv2.resize(image, (newW, newH))
    (H, W) = image.shape[:2]

    # define the two output layer names for the EAST detector model that
    # we are interested -- the first is the output probabilities and the
    # second can be used to derive the bounding box coordinates of text
    layerNames = ["feature_fusion/Conv_7/Sigmoid", "feature_fusion/concat_3"]

    # load the pre-trained EAST text detector
    net = get_east_model()

    # construct a blob from the image and then perform a forward pass of
    # the model to obtain the two output layer sets
    blob = cv2.dnn.blobFromImage(
        image, 1.0, (W, H), (123.68, 116.78, 103.94), swapRB=True, crop=False
    )
    net.setInput(blob)
    (scores, geometry) = net.forward(layerNames)

    # grab the number of rows and columns from the scores volume, then
    # initialize our set of bounding box rectangles and corresponding
    # confidence scores
    (numRows, numCols) = scores.shape[2:4]
    rects = []
    confidences = []

    # loop over the number of rows
    for y in range(0, numRows):
        # extract the scores (probabilities), followed by the geometrical
        # data used to derive potential bounding box coordinates that
        # surround text
        scoresData = scores[0, 0, y]
        xData0 = geometry[0, 0, y]
        xData1 = geometry[0, 1, y]
        xData2 = geometry[0, 2, y]
        xData3 = geometry[0, 3, y]
        anglesData = geometry[0, 4, y]

        # loop over the number of columns
        for x in range(0, numCols):
            # if our score does not have sufficient probability, ignore it
            if scoresData[x] < 0.99:
                continue

            # compute the offset factor as our resulting feature maps will
            # be 4x smaller than the input image
            (offsetX, offsetY) = (x * 4.0, y * 4.0)

            # extract the rotation angle for the prediction and then
            # compute the sin and cosine
            angle = anglesData[x]
            cos = np.cos(angle)
            sin = np.sin(angle)

            # use the geometry volume to derive the width and height of
            # the bounding box
            h = xData0[x] + xData2[x]
            w = xData1[x] + xData3[x]

            # compute both the starting and ending (x, y)-coordinates for
            # the text prediction bounding box
            endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
            endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
            startX = int(endX - w)
            startY = int(endY - h)

            # add the bounding box coordinates and probability score to
            # our respective lists
            rects.append((startX, startY, endX, endY))
            confidences.append(scoresData[x])

    # apply non-maxima suppression to suppress weak, overlapping bounding
    # boxes
    boxes = non_max_suppression(np.array(rects), probs=confidences)

    # loop over the bounding boxes
    surface = 0
    for (startX, startY, endX, endY) in boxes:
        # scale the bounding box coordinates based on the respective
        # ratios
        startX = int(startX * rW)
        startY = int(startY * rH)
        endX = int(endX * rW)
        endY = int(endY * rH)
        surface += (startY - startX) * (endY - endX)

        # draw the bounding box on the image
        cv2.rectangle(orig, (startX, startY), (endX, endY), (0, 255, 0), 2)

    return surface, orig


def detect_wcag_1_4_5_infractions(driver: WebDriver) -> List[AltTextInfraction]:
    """Detect WCAG 1.4.5 infractions in the given web page.

    Parameters
    ----------
    driver : WebDriver
        The web driver that contains the web page

    Returns
    -------
    List[ContrastInfraction]
        The detected infractions against WCAG 1.4.5
    """
    nondecorative, have_text, alts, els = find_decorative_and_nondecoratives(driver)

    infractions = []
    for src in nondecorative:
        if src in have_text:
            if not match_text(src, alts[src]):
                infractions.append(
                    AltTextInfraction(
                        wcag_criterion="WCAG_1_4_5",
                        xpath=get_xpath_of_element(els[src]),
                        text=alts[src],
                        type=1,  # 1 = error, 2 = warning
                    )
                )

    return infractions
