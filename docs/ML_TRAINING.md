# Machine Learning Models & Dataset Specifications

## 1. Salary Regression Model
- **Algorithm**: `GradientBoostingRegressor(n_estimators=120, max_depth=4, learning_rate=0.08)`
- **Dataset**: `job_postings_salary_dataset.csv` (1,500 realistic market entries)
- **Features**: `role`, `location`, `experience_years`, `skill_match_pct`, `skills_count`, `github_score`
- **Performance**: R² Score > 0.94, RMSE ~ 0.53 LPA

## 2. Career Trajectory Classification Model
- **Algorithm**: `MultiOutputClassifier(RandomForestClassifier(n_estimators=100, max_depth=6))`
- **Dataset**: `career_trajectory_dataset.csv` (1,800 transition paths)
- **Targets**: `ready_3m`, `ready_6m`, `ready_12m`
- **Features**: `target_role`, `current_readiness`, `experience_years`, `learning_hours_weekly`, `github_score`
