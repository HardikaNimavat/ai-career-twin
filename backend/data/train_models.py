import os
import json
import logging
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import GradientBoostingRegressor, RandomForestClassifier
from sklearn.multioutput import MultiOutputClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
DATASETS_DIR = os.path.join(DATA_DIR, "datasets")
MODELS_DIR = os.path.join(os.path.dirname(DATA_DIR), "ml_models")
os.makedirs(DATASETS_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

# -------------------------------------------------------------
# 1. GENERATE DATASET: Job Postings & Salaries (Location-Aware)
# -------------------------------------------------------------
def generate_salary_dataset(n_samples=1500):
    np.random.seed(42)
    roles = ["frontend", "backend", "fullstack", "data", "devops", "mobile"]
    locations = ["Ahmedabad", "Bangalore", "Mumbai", "Delhi-NCR", "Pune", "Hyderabad", "Remote"]
    
    loc_multipliers = {
        "Bangalore": 1.25,
        "Mumbai": 1.20,
        "Delhi-NCR": 1.15,
        "Hyderabad": 1.12,
        "Pune": 1.08,
        "Remote": 1.10,
        "Ahmedabad": 0.95
    }
    
    base_salaries = {
        "frontend": (4.5, 10.5),
        "backend": (5.0, 12.0),
        "fullstack": (5.5, 13.5),
        "data": (6.0, 16.0),
        "devops": (5.8, 14.5),
        "mobile": (4.8, 11.0)
    }

    records = []
    for _ in range(n_samples):
        role = np.random.choice(roles)
        loc = np.random.choice(locations)
        exp_years = np.clip(np.random.exponential(2.0), 0.0, 12.0)
        skill_match_pct = np.random.uniform(30.0, 98.0)
        skills_count = np.random.randint(2, 12)
        gh_score = np.clip(np.random.normal(55.0, 20.0), 10.0, 100.0)
        
        min_b, max_b = base_salaries[role]
        
        exp_factor = 1.0 + (exp_years * 0.18)
        match_factor = 0.5 + (skill_match_pct / 100.0) * 0.6
        gh_factor = 0.9 + (gh_score / 500.0)
        
        salary_lpa = min_b * exp_factor * match_factor * loc_multipliers[loc] * gh_factor
        salary_lpa += np.random.normal(0, salary_lpa * 0.05)
        salary_lpa = np.clip(salary_lpa, 3.2, 45.0)
        
        records.append({
            "role": role,
            "location": loc,
            "experience_years": exp_years,
            "skill_match_pct": np.round(skill_match_pct, 1),
            "skills_count": skills_count,
            "github_score": np.round(gh_score, 1),
            "salary_lpa": np.round(salary_lpa, 2)
        })
        
    df = pd.DataFrame(records)
    csv_path = os.path.join(DATASETS_DIR, "job_postings_salary_dataset.csv")
    df.to_csv(csv_path, index=False)
    logger.info("[+] Saved salary dataset: %s (%d records)", csv_path, len(df))
    return df

# -------------------------------------------------------------
# 2. GENERATE DATASET: Career Trajectory (3, 6, 12 Month Horizons)
# -------------------------------------------------------------
def generate_trajectory_dataset(n_samples=1800):
    np.random.seed(1337)
    roles = ["frontend", "backend", "fullstack", "data", "devops", "mobile"]
    
    records = []
    for _ in range(n_samples):
        role = np.random.choice(roles)
        current_readiness = np.random.uniform(20.0, 95.0)
        exp_years = np.clip(np.random.exponential(1.8), 0.0, 10.0)
        learning_hours_pw = np.random.uniform(5.0, 30.0)
        github_activity = np.random.uniform(20.0, 100.0)
        
        speed = (learning_hours_pw / 20.0) * 0.6 + (github_activity / 100.0) * 0.4
        
        gain_3m = speed * np.random.uniform(8.0, 16.0)
        r_3m = np.clip(current_readiness + gain_3m, 0, 100)
        prob_3m = int(r_3m >= 68)
        
        gain_6m = speed * np.random.uniform(18.0, 32.0)
        r_6m = np.clip(current_readiness + gain_6m, 0, 100)
        prob_6m = int(r_6m >= 75)
        
        gain_12m = speed * np.random.uniform(32.0, 55.0)
        r_12m = np.clip(current_readiness + gain_12m, 0, 100)
        prob_12m = int(r_12m >= 85)
        
        records.append({
            "target_role": role,
            "current_readiness": np.round(current_readiness, 1),
            "experience_years": np.round(exp_years, 1),
            "learning_hours_weekly": np.round(learning_hours_pw, 1),
            "github_score": np.round(github_activity, 1),
            "ready_3m": prob_3m,
            "ready_6m": prob_6m,
            "ready_12m": prob_12m
        })
        
    df = pd.DataFrame(records)
    csv_path = os.path.join(DATASETS_DIR, "career_trajectory_dataset.csv")
    df.to_csv(csv_path, index=False)
    logger.info("[+] Saved career trajectory dataset: %s (%d records)", csv_path, len(df))
    return df

# -------------------------------------------------------------
# 3. TRAIN AND SAVE ML MODELS
# -------------------------------------------------------------
def train_and_save_models():
    # 1. Salary Model
    df_salary = generate_salary_dataset()
    X_salary = pd.get_dummies(df_salary[["role", "location", "experience_years", "skill_match_pct", "skills_count", "github_score"]], drop_first=False)
    y_salary = df_salary["salary_lpa"]
    salary_features = list(X_salary.columns)
    
    X_train, X_test, y_train, y_test = train_test_split(X_salary, y_salary, test_size=0.15, random_state=42)
    model_salary = GradientBoostingRegressor(n_estimators=120, max_depth=4, learning_rate=0.08, random_state=42)
    model_salary.fit(X_train, y_train)
    
    r2 = r2_score(y_test, model_salary.predict(X_test))
    rmse = np.sqrt(mean_squared_error(y_test, model_salary.predict(X_test)))
    logger.info("[OK] Trained Salary Regression Model: R2 Score = %.3f, RMSE = %.2f LPA", r2, rmse)
    
    salary_bundle = {
        "model": model_salary,
        "features": salary_features,
        "r2_score": float(r2),
        "rmse": float(rmse)
    }
    salary_model_path = os.path.join(MODELS_DIR, "salary_model.joblib")
    joblib.dump(salary_bundle, salary_model_path)
    logger.info("[+] Saved Salary Model artifact: %s", salary_model_path)
    
    # 2. Career Trajectory Model
    df_traj = generate_trajectory_dataset()
    X_traj = pd.get_dummies(df_traj[["target_role", "current_readiness", "experience_years", "learning_hours_weekly", "github_score"]], drop_first=False)
    y_traj = df_traj[["ready_3m", "ready_6m", "ready_12m"]]
    traj_features = list(X_traj.columns)
    
    base_rf = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
    multi_model = MultiOutputClassifier(base_rf)
    multi_model.fit(X_traj, y_traj)
    
    traj_bundle = {
        "model": multi_model,
        "features": traj_features
    }
    traj_model_path = os.path.join(MODELS_DIR, "trajectory_model.joblib")
    joblib.dump(traj_bundle, traj_model_path)
    logger.info("[+] Saved Trajectory Model artifact: %s", traj_model_path)

if __name__ == "__main__":
    logger.info("========================================")
    logger.info("  Training AI Career Twin ML Models... ")
    logger.info("========================================")
    train_and_save_models()
    logger.info("========================================")
    logger.info("  All Datasets and Models Ready!       ")
    logger.info("========================================")
