import pandas as pd


def engineer_features(df):
    # Create Profit feature: Revenue - Budget
    df['profit'] = df['revenue'] - df['budget']

    # Create ROI (Return on Investment) feature. Avoid division by zero.
    df['ROI'] = df.apply(
        lambda row: (row['revenue'] / row['budget']) if row['budget'] > 0 else 0,
        axis=1
    )

    # Extract release year
    df['release_year'] = pd.to_datetime(df['release_date']).dt.year

    # Filter out movies with 0 budget or 0 revenue to clean up visual outliers
    df = df[(df['budget'] > 10000) & (df['revenue'] > 10000)]

    return df