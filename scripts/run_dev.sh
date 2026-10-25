#!/usr/bin/env bash
set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR/.."

echo "==================================================="
echo "  AI CAREER TWIN - Starting Development Server"
echo "==================================================="

if [ ! -f "backend/ml_models/salary_model.joblib" ]; then
    echo "[*] Training ML Models first..."
    python3 backend/data/train_models.py
fi

echo "[*] Launching FastAPI Web Application..."
python3 run.py
