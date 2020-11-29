from pathlib import Path

import numpy as np
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
            ("oem", 1, "--oem 1"),
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

    def test_string_method(self, cv_plate):
        plate_reader = LicencePlateOCRReader(image=cv_plate)

        assert "SZY 31113" in plate_reader.read_text()

    @pytest.mark.parametrize(
        "first_part_length,is_valid1",
        (
            (3, True),
            (2, True),
            (1, False),
            (4, False),
        ),
    )
    @pytest.mark.parametrize(
        "second_part_length,is_valid2",
        (
            (3, False),
            (4, True),
            (5, True),
        ),
    )
    @pytest.mark.parametrize(
        "separator,is_valid3",
        (
            (" ", True),
            ("-", True),
            ("_", False),
        ),
    )
    def test_check_regex_match_method(
        self,
        first_part_length,
        is_valid1,
        second_part_length,
        is_valid2,
        separator,
        is_valid3,
    ):
        plate_text = f"{'A' * first_part_length}{separator}{'B' * second_part_length}"
        print(plate_text, all([is_valid1, is_valid2, is_valid3]))
        lpor = LicencePlateOCRReader(np.ndarray([]))
        assert lpor.check_regex_match(plate_text) is all(
            [is_valid1, is_valid2, is_valid3]
        )
