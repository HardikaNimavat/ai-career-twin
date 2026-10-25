# AI Career Twin
> **An Intelligent System for Professional Profiling, Skill Gap Analysis & Career Trajectory Prediction**  
> *Indus University Software Group Project (CE0727) — 2025–2026*

---

## Overview

**AI Career Twin** constructs a computational digital model of a student's or developer's technical capabilities. Rather than acting as a generic chatbot wrapper, Twin integrates **real machine learning models, deterministic NLP taxonomies, location-aware compensation regressors, RAG resource indexes, and voice interview simulation** into an interactive developer dashboard.

---

## System Architecture

The application is structured into **3 core layers**:

```
+-------------------------------------------------------------------+
|                        PRESENTATION LAYER                         |
|   Interactive Dark Theme Dashboard · SVG Skill Constellation      |
|   Speech Recognition & Synthesis · Gap Visualizers · Dynamic Ring |
+---------------------------------+---------------------------------+
                                  | REST API & Static Mount
+---------------------------------v---------------------------------+
|                        AI & ML INTELLIGENCE LAYER                 |
|   1. Skill Extraction Engine (Gemini LLM + 50-Skill NLP Taxonomy) |
|   2. GitHub Maturity Engine (Quality Scoring 0-100 & Heuristics)  |
|   3. Semantic Gap Analyser (Cluster Affinity & Weighted Distance) |
|   4. Career Trajectory Predictor (scikit-learn Random Forest)     |
|   5. Location-Aware Salary Engine (Gradient Boosting Regressor)   |
|   6. RAG Roadmap Generator (Verified Platforms & Learning Paths)  |
|   7. AI Interview Simulator (Voice/Text Multidimensional Scoring) |
+---------------------------------+---------------------------------+
                                  |
+---------------------------------v---------------------------------+
|                         DATA INGESTION & DB                       |
|   SQLite / PostgreSQL (SQLAlchemy) · CSV Datasets · JSON Taxonomy |
+-------------------------------------------------------------------+
```

---

## Quick Start Guide

### 1. Open in VS Code
Open the project directory in VS Code:
```text
File -> Open Folder -> C:\Users\dell\.gemini\antigravity\scratch\ai-career-twin
```

### 2. Run with One Click
- **Option A**: Press **`F5`** in VS Code.
- **Option B**: Run `python run.py` in the terminal.
- **Option C**: Double click `scripts/run_dev.bat`.

### 3. Access the Web Dashboard
- **Web Application UI**: http://127.0.0.1:8000
- **Interactive Swagger REST API Docs**: http://127.0.0.1:8000/docs

---

## Project Structure

```
ai-career-twin/
├── .vscode/
│   ├── launch.json                   # One-click debugging for FastAPI & ML training
│   ├── settings.json                 # Python paths & workspace configs
│   └── extensions.json               # Recommended VS Code plugins
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/         # REST API routers (Profile, Gap, Trajectory, Salary, Interview, etc.)
│   │   ├── core/                     # App settings, environment vars, DB connection
│   │   ├── models/                   # SQLAlchemy database schemas
│   │   ├── schemas/                  # Pydantic data validation schemas
│   │   ├── services/                 # 9 AI/ML services (Gemini, GitHub, ML Predictors, Interview)
│   │   └── main.py                   # FastAPI server entry point & static frontend mount
│   ├── data/
│   │   ├── datasets/                 # CSV & JSON datasets (1,500+ records)
│   │   └── train_models.py           # scikit-learn model training script
│   ├── ml_models/                    # Trained .joblib binary artifacts
│   ├── requirements.txt              # Production dependencies
│   └── Dockerfile                    # Containerization for Railway / Render
├── frontend/
│   ├── index.html                    # Dashboard UI
│   ├── css/styles.css                # Dark theme design system
│   └── js/                           # Modular frontend controllers
├── docs/                             # Architecture, API & ML Documentation
├── scripts/                          # One-click startup scripts
├── run.py                            # Zero-config startup runner
├── docker-compose.yml
├── Procfile
└── README.md
```

---

## Completed Key Modules

1. **Module 1: Skill Extraction Engine**: Parses resume text using hybrid Gemini LLM and a 50-skill taxonomy with alias matching.
2. **Module 2: GitHub Intelligence Engine**: Computes Developer Maturity Score (0–100) and repository diagnostics without requiring API tokens.
3. **Module 3: Skill Gap Analyser**: Weighted semantic match scoring across 6 target roles.
4. **Module 4: Knowledge Graph**: Shortest learning path calculation via graph pathfinding.
5. **Module 5: Career Trajectory Predictor**: Multi-Output Random Forest predicting 3, 6, and 12-month job-readiness probabilities.
6. **Module 6: Location-Aware Salary Engine**: Gradient Boosting Regressor predicting LPA across Bangalore, Mumbai, Ahmedabad, Delhi-NCR, Pune, Hyderabad, and Remote.
7. **Module 7: RAG Roadmap Generator**: Verified course links, hours, and weekly milestones.
8. **Module 8: AI Interview Simulator**: Real-time Web Speech API voice transcription, speech synthesis, and AI evaluation on technical accuracy, clarity, and confidence.
9. **Module 9: Certificate Verifier**: Upload credentials to dynamically verify and update profile skill confidence.

---
*Created for Indus University Computer Science Engineering (7CSE-D)*
