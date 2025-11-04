"""
Computer Vision Model for Plant Disease Classification
Uses ResNet50 architecture for disease detection
"""

import torch
import torch.nn as nn
from torchvision import models, transforms
from typing import Dict, List, Optional, Union
import numpy as np
from pathlib import Path
from PIL import Image

from app.core.config import settings


class PlantDiseaseClassifier:
    """
    CV модель для классификации заболеваний растений

    Architecture: ResNet50 with custom classification head
    Input: RGB images (224x224)
    Output: Disease classification with confidence scores
    """

    # Supported disease classes
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

    # Russian translations
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

    # Disease descriptions (for detailed output)
    DISEASE_DESCRIPTIONS = {
        "healthy": "Растение здорово, признаков заболеваний не обнаружено",
        "powdery_mildew_tomato": "Грибковое заболевание, характеризующееся белым мучнистым налетом на листьях",
        "late_blight_tomato": "Опасное грибковое заболевание, поражающее листья, стебли и плоды",
        "leaf_spot_tomato": "Бактериальное или грибковое заболевание с характерными пятнами на листьях",
        "bacterial_spot_tomato": "Бактериальное заболевание с темными пятнами на листьях и плодах",
        "early_blight_tomato": "Грибковое заболевание с концентрическими кольцами на старых листьях",
        "septoria_leaf_spot": "Грибковое заболевание с мелкими круглыми пятнами с темными краями",
        "target_spot": "Грибковое заболевание с характерными мишеневидными пятнами",
        "tomato_yellow_leaf_curl_virus": "Вирусное заболевание, вызывающее скручивание и пожелтение листьев",
        "tomato_mosaic_virus": "Вирусное заболевание с мозаичным рисунком на листьях"
    }

    def __init__(self, model_path: Optional[Union[str, Path]] = None):
        """
        Initialize the classifier

        Args:
            model_path: Path to pretrained model weights (optional)
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"🔧 Using device: {self.device}")

        self.model = self._build_model()

        weights_path = self._resolve_weights_path(model_path)

        if weights_path and weights_path.exists():
            self._load_weights(weights_path)
        else:
            if weights_path:
                print(
                    f"⚠️ Custom weights not found at {weights_path}. "
                    "Using pretrained ImageNet weights."
                )
            else:
                print(
                    "⚠️ No custom weights path configured. "
                    "Using pretrained ImageNet weights."
                )

        # Image preprocessing pipeline
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],  # ImageNet means
                std=[0.229, 0.224, 0.225]  # ImageNet stds
            )
        ])

    def _build_model(self) -> nn.Module:
        """
        Build ResNet50 model with custom classification head

        Returns:
            PyTorch model
        """
        print("🏗️ Building ResNet50 model...")

        # Load pretrained ResNet50
        model = models.resnet50(weights='IMAGENET1K_V1')

        # Replace final fully connected layer
        num_features = model.fc.in_features
        model.fc = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(num_features, len(self.DISEASE_CLASSES))
        )

        # Move to device
        model = model.to(self.device)
        model.eval()

        print(f"✓ Model built with {len(self.DISEASE_CLASSES)} output classes")
        return model

    def _resolve_weights_path(
            self,
            model_path: Optional[Union[str, Path]]
    ) -> Optional[Path]:
        """Resolve the path to the custom model weights."""
        if model_path:
            return Path(model_path)

        if settings.CV_MODEL_PATH:
            return Path(settings.CV_MODEL_PATH)

        return None

    def _load_weights(self, path: str):
        """
        Load pretrained weights

        Args:
            path: Path to weight file (.pth)
        """
        try:
            print(f"📥 Loading weights from {path}...")
            state_dict = torch.load(path, map_location=self.device)
            self.model.load_state_dict(state_dict)
            print("✓ Weights loaded successfully")
        except FileNotFoundError:
            print(f"⚠️ Weight file not found: {path}")
        except RuntimeError as e:
            print(f"⚠️ Error loading weights: {e}")
            print("   Using pretrained ImageNet weights instead")
        except Exception as e:
            print(f"⚠️ Unexpected error loading weights: {e}")

    def predict(self, image: np.ndarray) -> Dict:
        """
        Predict disease from image

        Args:
            image: Input image as numpy array (RGB format)

        Returns:
            Dictionary containing:
                - predicted_class: Disease class name
                - disease_name: Disease name in Russian
                - confidence: Confidence score (0-1)
                - top3_predictions: Top 3 predictions with scores
                - all_probabilities: All class probabilities
                - description: Disease description
        """
        # Convert numpy array to PIL Image
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image.astype('uint8'), 'RGB')

        # Preprocess image
        img_tensor = self.transform(image).unsqueeze(0).to(self.device)

        # Inference
        with torch.no_grad():
            outputs = self.model(img_tensor)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probabilities, 1)

        # Get predicted class
        predicted_idx = predicted.item()
        predicted_class = self.DISEASE_CLASSES[predicted_idx]
        confidence_score = confidence.item()

        # Get top 3 predictions
        top3_prob, top3_idx = torch.topk(probabilities, min(3, len(self.DISEASE_CLASSES)))
        top3_predictions = [
            {
                "class": self.DISEASE_CLASSES[idx.item()],
                "name_ru": self.DISEASE_NAMES_RU[self.DISEASE_CLASSES[idx.item()]],
                "confidence": prob.item(),
                "description": self.DISEASE_DESCRIPTIONS[self.DISEASE_CLASSES[idx.item()]]
            }
            for prob, idx in zip(top3_prob[0], top3_idx[0])
        ]

        # Prepare result
        result = {
            "predicted_class": predicted_class,
            "disease_name": self.DISEASE_NAMES_RU[predicted_class],
            "confidence": confidence_score,
            "confidence_level": self._get_confidence_level(confidence_score),
            "description": self.DISEASE_DESCRIPTIONS[predicted_class],
            "top3_predictions": top3_predictions,
            "all_probabilities": probabilities[0].cpu().numpy().tolist(),
            "model_info": {
                "architecture": "ResNet50",
                "input_size": "224x224",
                "num_classes": len(self.DISEASE_CLASSES)
            }
        }

        return result

    def predict_batch(self, images: List[np.ndarray]) -> List[Dict]:
        """
        Predict diseases for multiple images

        Args:
            images: List of images as numpy arrays

        Returns:
            List of prediction dictionaries
        """
        results = []
        for image in images:
            result = self.predict(image)
            results.append(result)
        return results

    @staticmethod
    def _get_confidence_level(confidence: float) -> str:
        """
        Convert confidence score to human-readable level

        Args:
            confidence: Confidence score (0-1)

        Returns:
            Confidence level description
        """
        if confidence >= 0.95:
            return "очень высокая"
        elif confidence >= 0.85:
            return "высокая"
        elif confidence >= 0.75:
            return "средняя"
        elif confidence >= 0.60:
            return "низкая"
        else:
            return "очень низкая"

    def get_model_info(self) -> Dict:
        """
        Get model information

        Returns:
            Dictionary with model details
        """
        return {
            "architecture": "ResNet50",
            "framework": "PyTorch",
            "input_size": (224, 224, 3),
            "num_classes": len(self.DISEASE_CLASSES),
            "classes": self.DISEASE_CLASSES,
            "device": str(self.device),
            "trainable_params": sum(p.numel() for p in self.model.parameters() if p.requires_grad),
            "total_params": sum(p.numel() for p in self.model.parameters())
        }

    def save_model(self, path: str):
        """
        Save model weights

        Args:
            path: Path to save weights
        """
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        torch.save(self.model.state_dict(), path)
        print(f"✓ Model saved to {path}")

    def __repr__(self) -> str:
        return f"PlantDiseaseClassifier(classes={len(self.DISEASE_CLASSES)}, device={self.device})"


# Example usage
if __name__ == "__main__":
    # Initialize model
    model = PlantDiseaseClassifier()

    # Print model info
    info = model.get_model_info()
    print("\n📊 Model Information:")
    for key, value in info.items():
        print(f"  {key}: {value}")

    # Example prediction with dummy image
    dummy_image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    result = model.predict(dummy_image)

    print("\n🔍 Example Prediction:")
    print(f"  Disease: {result['disease_name']}")
    print(f"  Confidence: {result['confidence'] * 100:.2f}%")
    print(f"  Level: {result['confidence_level']}")