# API Documentation

## Authentication

All protected endpoints require JWT authentication.

### Get Access Token
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "password123"
}
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

## Diagnosis Endpoints

### Create Diagnosis
```http
POST /api/v1/diagnosis/
Authorization: Bearer {access_token}
Content-Type: multipart/form-data

image: [binary]
region: "Москва"
climate: "умеренно-континентальный"
plant_age: 45
use_reasoning: true
```

### Get Diagnosis History
```http
GET /api/v1/diagnosis/history?skip=0&limit=20
Authorization: Bearer {access_token}
```

### Get Diagnosis by ID
```http
GET /api/v1/diagnosis/{diagnosis_id}
Authorization: Bearer {access_token}
```

### Submit Feedback
```http
POST /api/v1/diagnosis/{diagnosis_id}/feedback
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "feedback_type": "accurate",
  "rating": 5,
  "comment": "Очень точный диагноз!"
}
```

## Analytics Endpoints

### Get Statistics
```http
GET /api/v1/analytics/statistics
Authorization: Bearer {access_token}
```

Response:
```json
{
  "total_diagnoses": 1234,
  "total_users": 567,
  "avg_confidence": 0.89,
  "most_common_diseases": [
    {
      "disease": "Мучнистая роса томатов",
      "count": 234
    }
  ]
}
```

## Rate Limiting

- 100 requests per hour per user
- 429 status code when limit exceeded
- Rate limit headers included in response

