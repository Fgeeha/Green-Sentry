import torch
import torch.nn as nn
from torchvision import models, transforms
from typing import Tuple, Dict
import numpy as np


class PlantDiseaseClassifier:
    """CV модель для классификации заболеваний растений"""

    DISEASE_CLASSES = [
        "healthy",
        "powdery_mildew_tomato",
        "late_blight_tomato",
        "leaf_spot_tomato",
        "bacterial_spot_tomato",
        "early_blight_tomato",
        "septoria_leaf_spot",
        "target_spot",
        "tomato_yellow_leaf_curl_virus",
        "tomato_mosaic_virus"
    ]

    DISEASE_NAMES_RU = {
        "healthy": "Здоровое растение",
        "powdery_mildew_tomato": "Мучнистая роса томатов",
        "late_blight_tomato": "Фитофтороз томатов",
        "leaf_spot_tomato": "Пятнистость листьев томатов",
        "bacterial_spot_tomato": "Бактериальная пятнистость томатов",
        "early_blight_tomato": "Альтернариоз томатов",
        "septoria_leaf_spot": "Септориоз листьев",
        "target_spot": "Кольцевая пятнистость",
        "tomato_yellow_leaf_curl_virus": "Вирус желтой курчавости листьев томата",
        "tomato_mosaic_virus": "Вирус мозаики томатов"
    }

    def __init__(self, model_path: str = None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self._build_model()

        if model_path:
            self._load_weights(model_path)

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

    def _build_model(self) -> nn.Module:
        """Создание модели на базе ResNet50"""
        model = models.resnet50(pretrained=True)
        num_features = model.fc.in_features
        model.fc = nn.Linear(num_features, len(self.DISEASE_CLASSES))
        model = model.to(self.device)
        model.eval()
        return model

    def _load_weights(self, path: str):
        """Загрузка весов модели"""
        try:
            self.model.load_state_dict(torch.load(path, map_location=self.device))
        except FileNotFoundError:
            print(f"⚠️ Веса модели не найдены: {path}. Используется предобученная модель.")

    def predict(self, image: np.ndarray) -> Dict:
        """
        Предсказание заболевания

        Args:
            image: Изображение в формате numpy array (RGB)

        Returns:
            Dict с результатами предсказания
        """
        from PIL import Image

        # Преобразование изображения
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)

        img_tensor = self.transform(image).unsqueeze(0).to(self.device)

        # Предсказание
        with torch.no_grad():
            outputs = self.model(img_tensor)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probabilities, 1)

        predicted_class = self.DISEASE_CLASSES[predicted.item()]
        confidence_score = confidence.item()

        # Топ-3 предсказания
        top3_prob, top3_idx = torch.topk(probabilities, 3)
        top3_predictions = [
            {
                "class": self.DISEASE_CLASSES[idx.item()],
                "name_ru": self.DISEASE_NAMES_RU[self.DISEASE_CLASSES[idx.item()]],
                "confidence": prob.item()
            }
            for prob, idx in zip(top3_prob[0], top3_idx[0])
        ]

        return {
            "predicted_class": predicted_class,
            "disease_name": self.DISEASE_NAMES_RU[predicted_class],
            "confidence": confidence_score,
            "top3_predictions": top3_predictions,
            "all_probabilities": probabilities[0].cpu().numpy().tolist()
        }