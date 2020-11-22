import string
from pathlib import Path
from typing import Optional

import numpy as np
import pytesseract
from cv2 import cv2 as cv2


class LicencePlateOCRReader:
    allowed_characters = string.ascii_uppercase + "0123456789"

    def __init__(
        self,
        image: np.ndarray = None,
        image_path: Optional[Path] = None,
        psm=6,
        osm=3,
        extra_config="",
    ):
        assert image is not None or image_path, "Provide image or image path"
        if image_path and not image_path.is_file():
            raise FileNotFoundError("Provided path does not exist or is directory")
        self.image = image if image is not None else cv2.imread(str(image_path))
        self.psm = psm
        self.osm = osm
        self.extra_config = extra_config

    def _get_config(self):
        return (
            f"--psm {self.psm} --osm {self.osm} {self.extra_config} "
            f"-c tessedit_char_whitelist={self.allowed_characters}"
        )

    def read_text(self) -> str:
        return pytesseract.image_to_string(self.image, config=self._get_config())
