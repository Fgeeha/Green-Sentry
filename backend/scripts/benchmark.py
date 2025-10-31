#!/usr/bin/env python
"""Benchmark model performance"""

import sys
from pathlib import Path
import time
import numpy as np
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.ml.cv_model import PlantDiseaseClassifier
from app.models.ml.reasoning_agent import DiseaseReasoningAgent
from app.utils.image_processor import ImageProcessor


def benchmark_cv_model(iterations: int = 100) -> Dict[str, float]:
    """Benchmark CV model"""
    print(f"\n🔬 Benchmarking CV Model ({iterations} iterations)...")

    model = PlantDiseaseClassifier()
    processor = ImageProcessor()

    # Load sample image
    sample_image = processor.load_and_preprocess("data/sample_images/tomato_leaf.jpg")

    times: List[float] = []

    for i in range(iterations):
        start = time.time()
        result = model.predict(sample_image)
        elapsed = time.time() - start
        times.append(elapsed)

        if (i + 1) % 10 == 0:
            print(f"  Progress: {i + 1}/{iterations}")

    return {
        "mean": np.mean(times),
        "median": np.median(times),
        "std": np.std(times),
        "min": np.min(times),
        "max": np.max(times),
        "p95": np.percentile(times, 95),
        "p99": np.percentile(times, 99),
    }


def benchmark_reasoning_agent(iterations: int = 10) -> Dict[str, float]:
    """Benchmark reasoning agent"""
    print(f"\n🧠 Benchmarking Reasoning Agent ({iterations} iterations)...")

    agent = DiseaseReasoningAgent()

    sample_cv_result = {
        "predicted_class": "powdery_mildew_tomato",
        "disease_name": "Мучнистая роса томатов",
        "confidence": 0.87,
        "top3_predictions": []
    }

    times: List[float] = []

    for i in range(iterations):
        start = time.time()
        result = agent.analyze_disease(
            cv_result=sample_cv_result,
            region="Москва",
            climate="умеренно-континентальный"
        )
        elapsed = time.time() - start
        times.append(elapsed)

        print(f"  Progress: {i + 1}/{iterations}")

    return {
        "mean": np.mean(times),
        "median": np.median(times),
        "std": np.std(times),
        "min": np.min(times),
        "max": np.max(times),
    }


def print_results(name: str, results: Dict[str, float]) -> None:
    """Print benchmark results"""
    print(f"\n📊 {name} Results:")
    print(f"  Mean:   {results['mean']:.3f}s")
    print(f"  Median: {results['median']:.3f}s")
    print(f"  Std:    {results['std']:.3f}s")
    print(f"  Min:    {results['min']:.3f}s")
    print(f"  Max:    {results['max']:.3f}s")
    if 'p95' in results:
        print(f"  P95:    {results['p95']:.3f}s")
        print(f"  P99:    {results['p99']:.3f}s")


def main():
    """Run all benchmarks"""
    print("🚀 Starting Benchmarks...")

    # CV Model
    cv_results = benchmark_cv_model(iterations=100)
    print_results("CV Model", cv_results)

    # Reasoning Agent
    reasoning_results = benchmark_reasoning_agent(iterations=10)
    print_results("Reasoning Agent", reasoning_results)

    # Total pipeline estimation
    total_mean = cv_results['mean'] + reasoning_results['mean']
    print(f"\n⏱️  Estimated Total Pipeline Time: {total_mean:.3f}s")
    print(f"   Throughput: ~{1 / total_mean:.2f} req/s")

    print("\n✅ Benchmarks completed!")


if __name__ == "__main__":
    main()