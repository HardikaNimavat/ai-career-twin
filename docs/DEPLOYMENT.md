# Deployment Guide — AI Career Twin

## Option 1: Docker (Single Container)
```bash
docker build -t ai-career-twin -f backend/Dockerfile .
docker run -p 8000:8000 ai-career-twin
```

## Option 2: Docker Compose
```bash
docker-compose up -d --build
```

## Option 3: Railway / Render
1. Push project to a GitHub repository.
2. Select "Deploy from GitHub repo".
3. Railway automatically detects `Dockerfile` or `Procfile`.
4. Set environment variables (`GEMINI_API_KEY`, etc.).
