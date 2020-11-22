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

    @pytest.mark.parametrize(
        "arg_name,value,expected_config",
        (
            ("osm", 1, "--osm 1"),
            ("psm", 2, "--psm 2"),
            (
                "extra_config",
                "--test y --check y" "--test 1 --check y",
                "--test y --check y" "--test 1 --check y",
            ),
        ),
    )
    def test_args_are_passed_to_tesseract_config(
        self, plate_path, arg_name, value, expected_config
    ):
        plate_reader = LicencePlateOCRReader(
            image_path=Path(plate_path), **{arg_name: value}
        )

        assert expected_config in plate_reader._get_config()
