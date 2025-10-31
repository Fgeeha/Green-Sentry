#!/usr/bin/env python
"""Download pre-trained models"""

import sys
from pathlib import Path
import requests
from tqdm import tqdm

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings


def download_file(url: str, destination: Path) -> None:
    """Download file with progress bar"""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))

    destination.parent.mkdir(parents=True, exist_ok=True)

    with open(destination, 'wb') as file, tqdm(
            desc=destination.name,
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
    ) as progress_bar:
        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            progress_bar.update(size)


def main():
    """Download all required models"""
    print("📥 Downloading models...")

    models = [
        {
            "name": "ResNet50 Plant Disease",
            "url": "https://example.com/models/plant_disease_resnet50.pth",
            "path": Path(settings.CV_MODEL_PATH)
        }
    ]

    for model in models:
        print(f"\nDownloading {model['name']}...")
        try:
            download_file(model['url'], model['path'])
            print(f"✓ {model['name']} downloaded successfully")
        except Exception as e:
            print(f"❌ Error downloading {model['name']}: {e}")

    print("\n✅ All models downloaded!")


if __name__ == "__main__":
    main()