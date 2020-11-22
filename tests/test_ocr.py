from pathlib import Path

import pytest

from platonic_io.ocr import LicencePlateOCRReader


class TestLicencePlateOCRReader:
    def test_image_or_image_path_are_required(self, cv_plate):
        with pytest.raises(AssertionError) as e:
            LicencePlateOCRReader()
        assert str(e.value) == "Provide image or image path"

    @pytest.mark.parametrize("path", ("/tmp", "/tmp/nonexistingimage.png"))
    def test_raises_error_when_missing_file(self, path):
        with pytest.raises(FileNotFoundError):
            LicencePlateOCRReader(image_path=Path(path))
