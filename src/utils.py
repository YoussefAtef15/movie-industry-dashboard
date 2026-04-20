import pandas as pd
from src.data_cleaning import clean_data
from src.feature_engineering import engineer_features


def process_pipeline(raw_path, clean_path):
    # Load Dataset
    print("Loading raw data...")
    df = pd.read_csv(raw_path)

    # Clean
    print("Cleaning data...")
    df = clean_data(df)

    # Engineer
    print("Engineering features...")
    df = engineer_features(df)

    # Save Clean Data
    print(f"Saving cleaned data to {clean_path}...")
    df.to_csv(clean_path, index=False)
    print("Data processing complete.")