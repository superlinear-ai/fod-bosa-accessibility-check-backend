"""Useful type aliases for neat typing."""

from typing import Dict, Union

import numpy as np

Image = np.ndarray
Infraction = Dict[str, Union[str, float]]
RGBColor = np.ndarray
