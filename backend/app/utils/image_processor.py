import cv2
import numpy as np
from PIL import Image
from pathlib import Path
from typing import Union, Tuple, Optional
import hashlib


class ImageProcessor:
    """Utility class for image loading and preprocessing"""

    def __init__(self, target_size: Tuple[int, int] = (224, 224)):
        """
        Initialize image processor

        Args:
            target_size: Target size for resizing images (width, height)
        """
        self.target_size = target_size

    def load_and_preprocess(
            self,
            image_path: Union[str, Path],
            enhance: bool = True
    ) -> np.ndarray:
        """
        Load and preprocess image from file

        Args:
            image_path: Path to image file
            enhance: Whether to apply image enhancement

        Returns:
            Preprocessed image as numpy array (RGB)
        """
        # Load image
        image = Image.open(image_path).convert('RGB')
        image_np = np.array(image)

        # Apply enhancement if requested
        if enhance:
            image_np = self.enhance_image(image_np)

        return image_np

    @staticmethod
    def enhance_image(image: np.ndarray) -> np.ndarray:
        """
        Enhance image quality using CLAHE (Contrast Limited Adaptive Histogram Equalization)

        Args:
            image: Input image (RGB)

        Returns:
            Enhanced image
        """
        # Convert RGB to LAB color space
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)

        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l_enhanced = clahe.apply(l)

        # Merge channels back
        enhanced_lab = cv2.merge([l_enhanced, a, b])
        enhanced_rgb = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2RGB)

        return enhanced_rgb

    @staticmethod
    def resize_image(
            image: np.ndarray,
            size: Tuple[int, int],
            keep_aspect_ratio: bool = False
    ) -> np.ndarray:
        """
        Resize image to target size

        Args:
            image: Input image
            size: Target size (width, height)
            keep_aspect_ratio: Whether to maintain aspect ratio

        Returns:
            Resized image
        """
        if keep_aspect_ratio:
            # Calculate aspect ratio
            h, w = image.shape[:2]
            target_w, target_h = size

            # Calculate scaling factor
            scale = min(target_w / w, target_h / h)
            new_w, new_h = int(w * scale), int(h * scale)

            # Resize image
            resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)

            # Create canvas and paste resized image
            canvas = np.zeros((target_h, target_w, 3), dtype=np.uint8)
            y_offset = (target_h - new_h) // 2
            x_offset = (target_w - new_w) // 2
            canvas[y_offset:y_offset + new_h, x_offset:x_offset + new_w] = resized

            return canvas
        else:
            return cv2.resize(image, size, interpolation=cv2.INTER_LANCZOS4)

    @staticmethod
    def normalize_image(image: np.ndarray) -> np.ndarray:
        """
        Normalize image to [0, 1] range

        Args:
            image: Input image

        Returns:
            Normalized image
        """
        return image.astype(np.float32) / 255.0

    @staticmethod
    def calculate_image_hash(image_path: Union[str, Path]) -> str:
        """
        Calculate SHA256 hash of image file

        Args:
            image_path: Path to image file

        Returns:
            Hex string of image hash
        """
        with open(image_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()

    @staticmethod
    def validate_image(image_path: Union[str, Path]) -> bool:
        """
        Validate if file is a valid image

        Args:
            image_path: Path to image file

        Returns:
            True if valid image, False otherwise
        """
        try:
            img = Image.open(image_path)
            img.verify()
            return True
        except Exception:
            return False

    @staticmethod
    def get_image_info(image_path: Union[str, Path]) -> dict:
        """
        Get image metadata

        Args:
            image_path: Path to image file

        Returns:
            Dictionary with image information
        """
        img = Image.open(image_path)

        return {
            "format": img.format,
            "mode": img.mode,
            "size": img.size,
            "width": img.width,
            "height": img.height,
            "file_size": Path(image_path).stat().st_size,
            "hash": ImageProcessor.calculate_image_hash(image_path)
        }

    @staticmethod
    def remove_background(image: np.ndarray) -> np.ndarray:
        """
        Remove background using color thresholding (for green plants)

        Args:
            image: Input image (RGB)

        Returns:
            Image with background removed
        """
        # Convert to HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)

        # Define range for green color (plants)
        lower_green = np.array([25, 40, 40])
        upper_green = np.array([90, 255, 255])

        # Create mask
        mask = cv2.inRange(hsv, lower_green, upper_green)

        # Apply morphological operations to clean up mask
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)

        # Apply mask to image
        result = cv2.bitwise_and(image, image, mask=mask)

        return result

    @staticmethod
    def adjust_brightness_contrast(
            image: np.ndarray,
            brightness: int = 0,
            contrast: int = 0
    ) -> np.ndarray:
        """
        Adjust brightness and contrast

        Args:
            image: Input image
            brightness: Brightness adjustment (-100 to 100)
            contrast: Contrast adjustment (-100 to 100)

        Returns:
            Adjusted image
        """
        if brightness != 0:
            if brightness > 0:
                shadow = brightness
                highlight = 255
            else:
                shadow = 0
                highlight = 255 + brightness
            alpha_b = (highlight - shadow) / 255
            gamma_b = shadow

            image = cv2.addWeighted(image, alpha_b, image, 0, gamma_b)

        if contrast != 0:
            f = 131 * (contrast + 127) / (127 * (131 - contrast))
            alpha_c = f
            gamma_c = 127 * (1 - f)

            image = cv2.addWeighted(image, alpha_c, image, 0, gamma_c)

        return image

    @staticmethod
    def rotate_image(image: np.ndarray, angle: float) -> np.ndarray:
        """
        Rotate image by given angle

        Args:
            image: Input image
            angle: Rotation angle in degrees

        Returns:
            Rotated image
        """
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)

        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h))

        return rotated