import numpy as np
import pytest
from cv2 import cv2 as cv2


@pytest.fixture
def plate_path():
    return "tests/test_data/plate1"


@pytest.fixture
def cv_plate(plate_path) -> np.ndarray:
    return cv2.imread(plate_path)
