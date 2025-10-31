
# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Upload  │  │ Results  │  │ History  │  │Analytics │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────┬───────────────────────────────────┘
                          │ REST API
┌─────────────────────────▼───────────────────────────────────┐
│                    Nginx (Reverse Proxy)                     │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    FastAPI Backend                           │
│  ┌────────────────────────────────────────────────────┐     │
│  │               API Layer                             │     │
│  │  - Authentication  - Validation  - Rate Limiting   │     │
│  └────────────────────────────────────────────────────┘     │
│  ┌────────────────────────────────────────────────────┐     │
│  │               Service Layer                         │     │
│  │  - Business Logic  - Orchestration                 │     │
│  └────────────────────────────────────────────────────┘     │
│  ┌────────────────────────────────────────────────────┐     │
│  │               Repository Layer                      │     │
│  │  - Data Access  - CRUD Operations                  │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
┌─────────▼────┐  ┌──────▼──────┐  ┌────▼────┐
│  PostgreSQL  │  │    Redis    │  │ Celery  │
│  (Database)  │  │   (Cache)   │  │ Workers │
└──────────────┘  └─────────────┘  └─────────┘
```

## ML Pipeline

```
┌──────────┐
│  Image   │
└────┬─────┘
     │
     ▼
┌──────────────────┐
│  Preprocessing   │
│  - Resize        │
│  - Normalize     │
│  - Enhance       │
└────┬─────────────┘
     │
     ▼
┌──────────────────┐
│  CV Model        │
│  (ResNet50)      │
│  - Classification│
│  - Confidence    │
└────┬─────────────┘
     │
     ├─────────────────┐
     │                 │
     ▼                 ▼
┌─────────┐      ┌──────────────┐
│ Cache   │      │  Reasoning   │
│ Check   │      │  Agent       │
│         │      │  (GigaChat)  │
└─────────┘      └──────┬───────┘
                        │
                        ▼
                 ┌──────────────┐
                 │  Response    │
                 │  Generation  │
                 └──────────────┘
```

## Database Schema

```sql
users
  - id (PK)
  - email (unique)
  - username (unique)
  - hashed_password
  - role (enum)
  - is_active
  - created_at

diagnoses
  - id (PK)
  - user_id (FK)
  - image_path
  - image_hash
  - predicted_class
  - disease_name
  - confidence
  - cv_results (JSON)
  - reasoning_results (JSON)
  - region
  - climate
  - created_at

feedbacks
  - id (PK)
  - diagnosis_id (FK)
  - user_id (FK)
  - feedback_type (enum)
  - rating
  - comment
  - created_at
```

## Security Layers

1. **Authentication**: JWT tokens
2. **Authorization**: Role-based access control
3. **Rate Limiting**: Redis-based limiter
4. **Input Validation**: Pydantic schemas
5. **SQL Injection**: SQLAlchemy ORM
6. **XSS Protection**: Content Security Policy
7. **CORS**: Configured origins