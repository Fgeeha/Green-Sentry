#!/usr/bin/env python
"""Seed database with sample data"""

import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.database.user import User, UserRole
from app.models.database.diagnosis import Diagnosis
from app.core.security import get_password_hash
import random
from datetime import datetime, timedelta


def create_users(db: Session) -> list[User]:
    """Create sample users"""
    users = [
        User(
            email="admin@example.com",
            username="admin",
            hashed_password=get_password_hash("admin123"),
            full_name="Admin User",
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True,
        ),
        User(
            email="user@example.com",
            username="user",
            hashed_password=get_password_hash("user123"),
            full_name="Regular User",
            role=UserRole.USER,
            is_active=True,
            is_verified=True,
        ),
        User(
            email="expert@example.com",
            username="expert",
            hashed_password=get_password_hash("expert123"),
            full_name="Expert User",
            role=UserRole.EXPERT,
            is_active=True,
            is_verified=True,
        ),
    ]

    for user in users:
        db.add(user)
    db.commit()

    for user in users:
        db.refresh(user)

    return users


def create_diagnoses(db: Session, users: list[User]) -> None:
    """Create sample diagnoses"""
    diseases = [
        ("powdery_mildew_tomato", "Мучнистая роса томатов"),
        ("late_blight_tomato", "Фитофтороз томатов"),
        ("early_blight_tomato", "Альтернариоз томатов"),
        ("healthy", "Здоровое растение"),
    ]

    regions = ["Москва", "Санкт-Петербург", "Краснодар", "Новосибирск"]
    climates = ["умеренно-континентальный", "континентальный", "субтропический"]

    for _ in range(50):
        user = random.choice(users)
        disease = random.choice(diseases)

        diagnosis = Diagnosis(
            user_id=user.id,
            image_path=f"uploads/sample_{random.randint(1000, 9999)}.jpg",
            image_hash=f"hash_{random.randint(10000, 99999)}",
            predicted_class=disease[0],
            disease_name=disease[1],
            confidence=random.uniform(0.7, 0.99),
            cv_results={
                "top3_predictions": [
                    {"class": disease[0], "name_ru": disease[1], "confidence": random.uniform(0.7, 0.99)},
                    {"class": "healthy", "name_ru": "Здоровое растение", "confidence": random.uniform(0.01, 0.3)},
                ]
            },
            region=random.choice(regions),
            climate=random.choice(climates),
            plant_age=random.randint(20, 90),
            reasoning_enabled=random.choice([True, False]),
            reasoning_results={
                "disease_stage": random.choice(["начальная", "средняя", "критическая"]),
                "spread_forecast": random.choice(["низкий", "средний", "высокий"]),
            },
            processing_time=random.uniform(1.0, 5.0),
            pipeline_version="v1.0-reasoning",
            created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
        )
        db.add(diagnosis)

    db.commit()


def main():
    """Main seeding function"""
    print("🌱 Seeding database...")

    db = SessionLocal()

    try:
        # Create users
        print("Creating users...")
        users = create_users(db)
        print(f"✓ Created {len(users)} users")

        # Create diagnoses
        print("Creating diagnoses...")
        create_diagnoses(db, users)
        print("✓ Created 50 diagnoses")

        print("\n✅ Database seeded successfully!")
        print("\nTest credentials:")
        print("  Admin: admin@example.com / admin123")
        print("  User: user@example.com / user123")
        print("  Expert: expert@example.com / expert123")

    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()