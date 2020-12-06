import re
import string
from pathlib import Path
from typing import Optional

import numpy as np
import pytesseract
from cv2 import cv2 as cv2


class LicencePlateOCRReader:
    allowed_characters = string.ascii_uppercase + "0123456789" + " -"
    license_plate_regex = r"([a-zA-Z]){2,3}[\- ]?([a-zA-Z0-9]){4,5}"

    def __init__(
        self,
        image: np.ndarray = None,
        image_path: Optional[Path] = None,
        psm=6,
        oem=3,
        extra_config="",
    ):
        assert image is not None or image_path, "Provide image or image path"
        if image_path and not image_path.is_file():
            raise FileNotFoundError("Provided path does not exist or is directory")
        self.image = image if image is not None else cv2.imread(str(image_path))
        self.psm = psm
        self.oem = oem
        self.extra_config = extra_config

    def _get_config(self):
        return (
            f"--psm {self.psm} --oem {self.oem} {self.extra_config} "
            f"-c tessedit_char_whitelist='{self.allowed_characters}'"
        )

    def read_text(self) -> str:
        raw_text = pytesseract.image_to_string(self.image, config=self._get_config())
        return raw_text.strip()

    def check_regex_match(self, plate_text) -> bool:
        return bool(re.match(self.license_plate_regex, plate_text))
