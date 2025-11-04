from app.models.cv_model import PlantDiseaseClassifier
from app.models.reasoning_agent import DiseaseReasoningAgent
from app.utils.image_processor import ImageProcessor
from typing import Dict, Optional
import numpy as np


class DiagnosticPipeline:
    """Полный pipeline диагностики с reasoning-компонентом"""

    def __init__(
            self,
            cv_model_path: Optional[str] = None,
            gigachat_api_key: Optional[str] = None
    ):
        self.cv_model = PlantDiseaseClassifier(cv_model_path)
        self.reasoning_agent = DiseaseReasoningAgent(gigachat_api_key)
        self.image_processor = ImageProcessor()

    def diagnose(
            self,
            image_path: str,
            region: str = None,
            climate: str = None,
            plant_age: Optional[int] = None,
            additional_context: Optional[str] = None,
            use_reasoning: bool = True
    ) -> Dict:
        """
        Полная диагностика заболевания растения

        Args:
            image_path: Путь к изображению
            region: Регион выращивания
            climate: Климатическая зона
            plant_age: Возраст растения
            additional_context: Дополнительная информация
            use_reasoning: Использовать ли reasoning-агент

        Returns:
            Полный результат диагностики
        """
        # Этап 1: Обработка изображения
        image = self.image_processor.load_and_preprocess(image_path)

        # Этап 1.1: Проверка наличия растения на изображении
        image_analysis = self.image_processor.detect_plant_presence(image)

        if not image_analysis["is_plant"]:
            return {
                "pipeline_version": "v1.0-non-plant",
                "cv_result": None,
                "reasoning_analysis": None,
                "report": self._generate_non_plant_report(image_analysis),
                "image_analysis": image_analysis
            }

        # Этап 2: CV-диагностика
        cv_result = self.cv_model.predict(image)

        # Этап 3: Reasoning-анализ (опционально)
        if use_reasoning:
            analysis = self.reasoning_agent.analyze_disease(
                cv_result=cv_result,
                region=region,
                climate=climate,
                plant_age=plant_age,
                additional_context=additional_context
            )

            # Генерация отчета
            report = self.reasoning_agent.generate_report(analysis)

            return {
                "pipeline_version": "v1.0-reasoning",
                "cv_result": cv_result,
                "reasoning_analysis": analysis,
                "report": report,
                "image_analysis": image_analysis
            }
        else:
            return {
                "pipeline_version": "v1.0-basic",
                "cv_result": cv_result,
                "report": self._generate_basic_report(cv_result),
                "image_analysis": image_analysis
            }

    def _generate_basic_report(self, cv_result: Dict) -> str:
        """Базовый отчет без reasoning"""
        return f"""
            Диагноз: {cv_result['disease_name']}
            Уверенность: {cv_result['confidence'] * 100:.1f}%
            
            Топ-3 предсказания:
            {chr(10).join([f"{i + 1}. {p['name_ru']} - {p['confidence'] * 100:.1f}%" for i, p in enumerate(cv_result['top3_predictions'])])}
            """

    @staticmethod
    def _generate_non_plant_report(image_analysis: Dict) -> str:
        """Формирование отчета, если на изображении не найдено растение"""
        green_ratio = image_analysis.get("green_pixel_ratio", 0) * 100
        return (
            "На загруженном изображении не обнаружено растения. "
            "Попробуйте загрузить фото растения с минимальным количеством фона. "
            f"Доля растительной области: {green_ratio:.1f}%."
        )