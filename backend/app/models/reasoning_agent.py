import hashlib
import json
from pathlib import Path
from typing import Optional, Tuple, Union

import cv2
import numpy as np
from gigachat import GigaChat
from PIL import Image

from app.core.config import settings


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


class DiseaseReasoningAgent:
    """Reasoning-агент на базе GigaChat для анализа заболеваний"""

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or settings.GIGACHAT_API_KEY
        self.client = GigaChat(
            credentials=self.api_key,
            model=settings.GIGACHAT_MODEL,
            verify_ssl_certs=False,
        )

    def analyze_disease(
            self,
            cv_result: dict,
            region: str = None,
            climate: str = None,
            plant_age: Optional[int] = None,
            additional_context: Optional[str] = None
    ) -> dict:
        """
        Глубокий анализ заболевания с помощью reasoning

        Args:
            cv_result: Результат от CV-модели
            region: Регион выращивания
            climate: Климатическая зона
            plant_age: Возраст растения в днях
            additional_context: Дополнительная информация

        Returns:
            Структурированный анализ заболевания
        """
        region = region or settings.DEFAULT_REGION
        climate = climate or settings.DEFAULT_CLIMATE

        prompt = self._build_prompt(
            cv_result, region, climate, plant_age, additional_context
        )

        try:
            response = self.client.chat(prompt)
            analysis = self._parse_response(response.choices[0].message.content)

            return {
                "success": True,
                "cv_diagnosis": cv_result,
                "reasoning_analysis": analysis,
                "metadata": {
                    "region": region,
                    "climate": climate,
                    "plant_age": plant_age
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "cv_diagnosis": cv_result
            }

    def _build_prompt(
            self,
            cv_result: dict,
            region: str,
            climate: str,
            plant_age: Optional[int],
            additional_context: Optional[str]
    ) -> str:
        """Формирование промпта для GigaChat"""

        disease_name = cv_result.get("disease_name", "Неизвестное заболевание")
        confidence = cv_result.get("confidence", 0) * 100
        top3 = cv_result.get("top3_predictions", [])

        prompt = f"""Ты - эксперт-фитопатолог с 20-летним опытом работы. 
Проанализируй результаты диагностики заболевания растения и дай подробное заключение.

ДАННЫЕ ДИАГНОСТИКИ:
- Основной диагноз: {disease_name}
- Уверенность модели: {confidence:.1f}%
- Альтернативные диагнозы: {', '.join([f"{p['name_ru']} ({p['confidence'] * 100:.1f}%)" for p in top3[1:]])}

КОНТЕКСТ:
- Регион: {region}
- Климат: {climate}
- Возраст растения: {plant_age if plant_age else 'не указан'} дней
{f'- Дополнительная информация: {additional_context}' if additional_context else ''}

ЗАДАНИЕ:
Предоставь структурированный анализ в формате JSON со следующими полями:

1. "diagnosis_confirmation": Подтверждение или уточнение диагноза с учетом альтернативных версий
2. "disease_stage": Вероятная стадия развития заболевания (начальная/средняя/критическая)
3. "causes": Список основных причин возникновения заболевания в данных условиях
4. "risk_factors": Факторы риска, специфичные для региона и климата
5. "spread_forecast": Прогноз распространения заболевания (низкий/средний/высокий)
6. "treatment_plan": Детальный план лечения с конкретными препаратами и дозировками
7. "prevention": Профилактические меры для предотвращения рецидива
8. "regional_recommendations": Специфические рекомендации для региона {region}
9. "timeline": Временные рамки лечения
10. "success_probability": Вероятность успешного лечения (%)

Отвечай ТОЛЬКО валидным JSON без дополнительных объяснений."""

        return prompt

    def _parse_response(self, response: str) -> dict:
        """Парсинг ответа от GigaChat"""
        try:
            # Извлечение JSON из ответа
            json_start = response.find('{')
            json_end = response.rfind('}') + 1

            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            # Если JSON не найден, возвращаем текст как есть
            return {
                "raw_response": response,
                "parsed": False
            }
        except json.JSONDecodeError:
            return {
                "raw_response": response,
                "parsed": False,
                "error": "Failed to parse JSON response"
            }

    def generate_report(self, analysis: dict) -> str:
        """Генерация человеко-читаемого отчета"""
        if not analysis.get("success"):
            return f"❌ Ошибка анализа: {analysis.get('error', 'Unknown error')}"

        cv = analysis.get("cv_diagnosis", {})
        reasoning = analysis.get("reasoning_analysis", {})
        metadata = analysis.get("metadata", {})

        diagnosis = cv.get("disease_name", "Неизвестное заболевание")
        confidence = cv.get("confidence")
        top_predictions = cv.get("top3_predictions") or []

        alt_diagnoses = self._format_alternative_diagnoses(top_predictions)

        report_lines = [
            "╔══════════════════════════════════════════════════════════════╗",
            "║          ОТЧЕТ О ДИАГНОСТИКЕ ЗАБОЛЕВАНИЯ РАСТЕНИЯ            ║",
            "╚══════════════════════════════════════════════════════════════╝",
            "",
            "📊 РЕЗУЛЬТАТЫ КОМПЬЮТЕРНОГО ЗРЕНИЯ",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"🔍 Диагноз: {diagnosis}",
        ]

        if confidence is not None:
            report_lines.append(f"📈 Уверенность модели: {confidence * 100:.1f}%")

        report_lines.append("")
        report_lines.append("Альтернативные диагнозы:")
        report_lines.extend(alt_diagnoses or ["  • Недоступны"])

        if not reasoning.get("parsed", True) and reasoning.get("raw_response"):
            report_lines.extend(
                [
                    "",
                    "⚠️ Не удалось распарсить структурированный ответ модели.",
                    "Исходный текст:",
                    f"  {reasoning['raw_response']}",
                    "",
                ]
            )

        report_lines.extend(
            [
                "",
                "🧠 REASONING-АНАЛИЗ (GigaChat)",
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                self._format_key_value(
                    "✅ Подтверждение диагноза", reasoning.get("diagnosis_confirmation")
                ),
                self._format_key_value(
                    "📊 Стадия заболевания", reasoning.get("disease_stage")
                ),
                "",
                "🔬 Причины возникновения:",
            ]
        )

        report_lines.extend(
            self._format_list(reasoning.get("causes"))
        )

        report_lines.extend(
            [
                "",
                "⚠️ Факторы риска:",
            ]
        )
        report_lines.extend(
            self._format_list(reasoning.get("risk_factors"))
        )

        report_lines.extend(
            [
                "",
                self._format_key_value(
                    "📈 Прогноз распространения", reasoning.get("spread_forecast")
                ),
                "",
                "💊 ПЛАН ЛЕЧЕНИЯ",
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            ]
        )
        report_lines.extend(
            self._format_list(reasoning.get("treatment_plan"), indent="  • ")
        )

        report_lines.extend(
            [
                "",
                "🛡️ ПРОФИЛАКТИКА",
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            ]
        )
        report_lines.extend(
            self._format_list(reasoning.get("prevention"))
        )

        regional_recs = reasoning.get("regional_recommendations")
        region_name = metadata.get("region")
        if isinstance(regional_recs, dict):
            region_name = regional_recs.get("region", region_name)

        report_lines.extend(
            [
                "",
                f"🌍 РЕГИОНАЛЬНЫЕ РЕКОМЕНДАЦИИ ({region_name or 'Регион не указан'})",
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            ]
        )

        if isinstance(regional_recs, dict):
            for category, recs in regional_recs.items():
                if category == "region":
                    continue
                report_lines.append(f"{category.upper()}:")
                report_lines.extend(self._format_list(recs))
                report_lines.append("")
            if report_lines[-1] == "":
                report_lines.pop()
        else:
            report_lines.extend(
                self._format_list(regional_recs) or ["  • Рекомендации отсутствуют"]
            )

        report_lines.extend(
            [
                "",
                self._format_key_value("⏱️ Временные рамки", reasoning.get("timeline")),
                self._format_key_value(
                    "🎯 Вероятность успеха",
                    self._format_success_probability(reasoning.get("success_probability")),
                ),
                "",
                "╔══════════════════════════════════════════════════════════════╗",
                "║                    КОНЕЦ ОТЧЕТА                              ║",
                "╚══════════════════════════════════════════════════════════════╝",
            ]
        )

        return "\n".join(filter(None, report_lines))

    @staticmethod
    def _format_alternative_diagnoses(predictions: list) -> list:
        if not predictions or len(predictions) <= 1:
            return []

        formatted = []
        for idx, prediction in enumerate(predictions[1:], start=1):
            name = prediction.get("name_ru") or prediction.get("name") or "Неизвестно"
            confidence = prediction.get("confidence")
            if confidence is not None:
                formatted.append(f"  {idx}. {name} - {confidence * 100:.1f}%")
            else:
                formatted.append(f"  {idx}. {name}")
        return formatted

    @staticmethod
    def _format_list(values, indent: str = "  • ") -> list:
        if not values:
            return [f"{indent}Нет данных"]
        if isinstance(values, str):
            return [f"{indent}{values}"]
        formatted = []
        for item in values:
            if isinstance(item, dict):
                formatted.append(f"{indent}{json.dumps(item, ensure_ascii=False)}")
            else:
                formatted.append(f"{indent}{item}")
        return formatted

    @staticmethod
    def _format_key_value(title: str, value) -> str:
        if value in (None, ""):
            return f"{title}: Нет данных"
        return f"{title}: {value}"

    @staticmethod
    def _format_success_probability(value) -> str:
        if value in (None, ""):
            return "Нет данных"
        if isinstance(value, (int, float)):
            return f"{value:.0f}%"
        return str(value)