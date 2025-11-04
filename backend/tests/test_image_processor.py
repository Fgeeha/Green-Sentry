import numpy as np

from app.utils.image_processor import ImageProcessor


def test_detect_plant_presence_positive():
    image = np.full((224, 224, 3), (34, 139, 34), dtype=np.uint8)

    result = ImageProcessor.detect_plant_presence(image)

    assert result["is_plant"] is True
    assert result["green_pixel_ratio"] > 0.8


def test_detect_plant_presence_negative():
    image = np.full((224, 224, 3), 200, dtype=np.uint8)

    result = ImageProcessor.detect_plant_presence(image)

    assert result["is_plant"] is False
    assert result["green_pixel_ratio"] < 0.05