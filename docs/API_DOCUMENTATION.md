# REST API Documentation — AI Career Twin

FastAPI auto-generates interactive OpenAPI documentation at `/docs` and `/redoc`.

## Key Endpoints

### 1. `POST /api/v1/profile/parse`
Parses resume text, evaluates GitHub maturity, calculates gap analysis, generates roadmap, predicts salary, and returns the unified Digital Twin profile.

### 2. `POST /api/v1/predictor/trajectory`
Infers 3, 6, and 12-month qualification probabilities based on learning commitment and current readiness.

### 3. `POST /api/v1/salary/estimate`
Location-aware salary regression taking into account target role, experience, skill match percentage, and regional cost-of-living multiplier.

### 4. `POST /api/v1/interview/score`
Evaluates technical interview answers on Technical Accuracy (0-100), Clarity (0-100), and Confidence (0-100).

### 5. `POST /api/v1/certificate/verify`
Extracts credential keywords from uploaded certificates and validates credential level.
