from io import BytesIO
from pathlib import Path

import pytest
from PIL import Image
from pixelmatch.contrib.PIL import pixelmatch


def assert_image_matches(img_data, expected_filename, tolerance=0):
    """Compare image bytes to expected image file.  Raises a pytest error if
    images do not sufficiently match.

    Parameters
    ----------
    img_data : bytes
    expected_filename : str
    tolerance : int
        number of pixels that are allowed to be different
    """
    buffer = BytesIO(img_data)
    actual = Image.open(buffer)
    expected = Image.open(expected_filename)

    actual.save(f"/tmp/{Path(expected_filename).name}")

    if actual.size != expected.size:
        pytest.fail("image size does not match")

    diff = pixelmatch(actual, expected, includeAA=False, threshold=0.1285)

    if diff > tolerance:
        pytest.fail(f"{expected_filename} differs by {diff} pixels")
