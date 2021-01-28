"""Detect WCAG 1.4.11 infractions."""

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np
from imutils.object_detection import non_max_suppression
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from .type_aliases import Image, Infraction
from .utils import get_contrast_ratio, get_xpath_of_element

MIN_CONTRAST_RATIO = 4.5
MIN_CONTRAST_RATIO_LARGE_TEXT = 3.0


@dataclass
class BoundingBox:
    """Class representing a bounding box."""

    x1: int
    x2: int
    y1: int
    y2: int
    contrast: float
    contrast_threshold: float

    def __str__(self) -> str:
        """Return the string representation of a bounding box."""
        return ",".join([str(self.x1), str(self.x2), str(self.y1), str(self.y2)])


def detect_wcag_1_4_3_infractions(
    driver: WebDriver, img_small: Image, img_large: Image
) -> List[Infraction]:
    """Detect WCAG 1.4.3 infractions in the given web page.

    Parameters
    ----------
    driver : WebDriver
        The web driver that contains the web page
    img_small : Image
        A screenshot of the web page (taken by the given web driver)
    img_large : Image
        A retina screenshot of the web page

    Returns
    -------
    List[Infraction]
        The detected infractions against WCAG 1.4.3
    """
    new_width, new_height = get_new_size(img_small)
    img_large = cv2.resize(
        img_large, (new_width * 2, new_height * 2), interpolation=cv2.INTER_NEAREST
    )

    low_boxes = []
    bounding_boxes = compute_east_boxes(img_small)
    for box in bounding_boxes:
        contrast = get_contrast_ratio(
            img_large, round(box.x1 * 2), round(box.x2 * 2), round(box.y1 * 2), round(box.y2 * 2)
        )

        min_contrast = MIN_CONTRAST_RATIO if box.y2 - box.y1 < 20 else MIN_CONTRAST_RATIO_LARGE_TEXT
        if contrast < min_contrast and contrast >= 1.2:
            box.contrast = contrast
            box.contrast_threshold = min_contrast
            low_boxes.append(box)

    low_boxes = sorted(low_boxes, key=lambda b: [b.y1, b.x1])
    prev = -1
    for i, box in enumerate(low_boxes):
        if i > 0 and abs(box.y1 - prev) <= 3:
            box.y1 = prev
        prev = box.y1
        low_boxes = sorted(low_boxes, key=lambda b: [b.y1, b.x1])
    low_boxes = concatenate_words_horizontally(low_boxes)

    infractions_dict: Dict[str, Infraction] = {}
    for box in low_boxes:
        dom_element = get_dom_element(box, driver)
        if not dom_element:
            continue  # Continue if we can't find the DOM element

        xpath = get_xpath_of_element(dom_element)
        if xpath in infractions_dict:
            contrast_already_in_dict: float = infractions_dict[xpath]["contrast"]  # type: ignore
            if box.contrast > contrast_already_in_dict:
                continue  # Continue if the xpath is already in the dict with a lower contrast

        infraction: Infraction = {
            "wcag_criterion": "WCAG_1_4_3",
            "xpath": xpath,
            "contrast": box.contrast,
            "contrast_threshold": box.contrast_threshold,
        }
        infractions_dict[xpath] = infraction

    return list(infractions_dict.values())


def get_new_size(img: Image) -> Tuple[int, int]:
    """Compute the size of an image in multiples of 32.

    Parameters
    ----------
    img : Image
        The image we should compute the new size for

    Returns
    -------
    Tuple[int, int]
        The new width and new height of the image
    """
    return img.shape[1] + (32 - (img.shape[1] % 32)), img.shape[0] + (32 - (img.shape[0] % 32))


def compute_east_boxes(img: Image) -> List[BoundingBox]:
    """Compute text bounding boxes in the given image using the EAST model.

    Parameters
    ----------
    img : Image
        The screenshot in which we need to find the bounding boxes

    Returns
    -------
    List[BoundingBox]
        The bounding boxes which contain text
    """
    new_width, new_height = get_new_size(img)
    blob = cv2.dnn.blobFromImage(img, 1, (new_width, new_height))
    net = get_east_model()
    net.setInput(blob)
    layerNames = ["feature_fusion/Conv_7/Sigmoid", "feature_fusion/concat_3"]
    (scores, geometry) = net.forward(layerNames)

    (numRows, numCols) = scores.shape[2:4]
    rects = []
    confidences = []

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

        for x in range(0, numCols):
            # if our score does not have sufficient probability, ignore it
            if scoresData[x] < 0.8:
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

    boxes = non_max_suppression(np.array(rects), probs=confidences)
    return [BoundingBox(box[0], box[2], box[1], box[3], -1, -1) for box in boxes]


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


def concatenate_words_horizontally(boxes: List[BoundingBox]) -> List[BoundingBox]:
    """Try to concatenate words into lines.

    Parameters
    ----------
    boxes : List[BoundingBox]
        The bounding boxes we wish to concatenate

    Returns
    -------
    List[BoundingBox]
        The concatenated bounding boxes
    """
    concatenated_words: List[BoundingBox] = []
    for box in boxes:
        if not concatenated_words:
            concatenated_words.append(box)
            continue
        previous = concatenated_words[-1]
        line_height = previous.y2 - previous.y1
        diff_x = abs(box.x1 - previous.x2)  # concatenate if the x difference < line height
        diff_y1 = abs(box.y1 - previous.y1)  # concatenate if y1 difference < line height / 2
        diff_y2 = abs(box.y2 - previous.y2)  # concatenate if y2 difference < line height / 2
        if diff_x < line_height and diff_y1 < line_height / 2 and diff_y2 < line_height / 2:
            previous.contrast = min(previous.contrast, box.contrast)
            previous.x2 = box.x2
        else:
            concatenated_words.append(box)
    return concatenated_words


def get_dom_element(box: BoundingBox, driver: WebDriver) -> Optional[WebElement]:
    """Get the DOM element located at the coordinates of the given bounding box.

    Parameters
    ----------
    box : BoundingBox
        The bounding box for which we want to retrieve the DOM element
    driver : WebDriver
        The web driver that contains the web page

    Returns
    -------
    Optional[WebElement]
        The DOM element we potentially found
    """
    return driver.execute_script(
        "return document.elementFromPoint(arguments[0], arguments[1]);",
        int(box.x1 + (box.x2 - box.x1) / 2),
        int(box.y1 + (box.y2 - box.y1) / 2),
    )
