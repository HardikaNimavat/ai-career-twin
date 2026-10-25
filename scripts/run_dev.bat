@echo off
echo ===================================================
echo   AI CAREER TWIN - Starting Development Server
echo ===================================================
cd /d "%~dp0.."

if not exist "backend\ml_models\salary_model.joblib" (
    echo [*] Training ML Models first...
    python backend/data/train_models.py
)

echo [*] Launching FastAPI Web Application...
python run.py
pause
