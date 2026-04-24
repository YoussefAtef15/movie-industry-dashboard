import pandas as pd
from src.data_cleaning import clean_data
from src.feature_engineering import engineer_features


def validate_dataset(df):
    """
    Strict validation to ensure the dashboard dataset is complete.
    Raises a ValueError if ANY required column is missing.
    """
    required_columns = [
        'title', 'budget', 'revenue', 'profit', 'ROI', 'performance_status',
        'log_budget', 'log_revenue', 'release_year', 'release_month', 'release_day',
        'main_genre', 'runtime', 'vote_average', 'weighted_rating',
        'revenue_flag', 'language_group', 'popularity', 'popularity_score',
        'vote_count', 'primary_company', 'Decade', 'Decade_Str', 'Season',
        'Budget_Tier', 'Rating_Cat'
    ]

    missing_cols = [col for col in required_columns if col not in df.columns]

    if missing_cols:
        raise ValueError(
            f"\n[DATA VALIDATION ERROR]: The dataset is missing the following required columns:\n"
            f"{missing_cols}\n"
            f"-> ACTION REQUIRED: You must engineer these columns in your Jupyter Notebook "
            f"(or feature_engineering.py) BEFORE saving to 'cleaned_movies.csv'. "
            f"Do NOT create columns inside app.py."
        )
    print("[SUCCESS] Dataset validation passed. All required columns are present.")
    return True


def process_pipeline(raw_path, clean_path):
    """
    Executes the full data processing pipeline: Loading -> Cleaning -> Engineering -> Saving.
    """
    # 1. Load Dataset
    print("Loading raw data...")
    df = pd.read_csv(raw_path)

    # 2. Clean Data
    print("Cleaning data (Handling missing values, extracting genres, smart imputation)...")
    df = clean_data(df)

    # 3. Engineer Features
    print("Engineering features (Financial metrics, log transformations, weighted ratings)...")
    df = engineer_features(df)

    # 4. Save Clean Data
    print(f" Saving clean and lightweight data to {clean_path}...")
    df.to_csv(clean_path, index=False)
    print("Data processing pipeline complete. The dashboard is ready to use this data!")