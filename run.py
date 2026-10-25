import os
import sys
import logging

# Ensure project root is in Python search path
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("run")

if __name__ == "__main__":
    logger.info("=" * 65)
    logger.info("   AI CAREER TWIN - FULL-STACK WEB PLATFORM")
    logger.info("   Indus University Software Group Project (2025-2026)")
    logger.info("=" * 65)
    
    # 1. Verify ML Models Exist or Train them on startup
    model_path = os.path.join(ROOT, "backend", "ml_models", "salary_model.joblib")
    if not os.path.exists(model_path):
        logger.info("[*] Initializing & Training scikit-learn ML models from datasets...")
        from backend.data.train_models import train_and_save_models
        train_and_save_models()
        logger.info("[+] ML Models trained successfully!")

    # 2. Launch FastAPI with Uvicorn
    import uvicorn
    logger.info("[+] Starting Web Application Server at http://127.0.0.1:8000")
    logger.info("[+] Web Dashboard UI:  http://127.0.0.1:8000")
    logger.info("[+] Swagger API Docs:  http://127.0.0.1:8000/docs")
    logger.info("[*] Press Ctrl+C in terminal to stop server.")
    
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
