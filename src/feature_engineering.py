import pandas as pd
import numpy as np
import ast


def cap_outliers(df, col):
    """Caps extreme outliers using the IQR (Winsorization) method."""
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    df[col] = np.clip(df[col], lower, upper)
    return df


def get_primary_company(comp_str):
    """Extracts the first production company from the JSON string."""
    try:
        comps = ast.literal_eval(comp_str)
        return comps[0]['name'] if len(comps) > 0 else 'Unknown'
    except:
        return 'Unknown'


def get_season(month):
    """Maps release_month to a standard Season."""
    if pd.isna(month): return 'Unknown'
    month = int(month)
    if month in [12, 1, 2]:
        return 'Winter'
    elif month in [3, 4, 5]:
        return 'Spring'
    elif month in [6, 7, 8]:
        return 'Summer'
    else:
        return 'Autumn'  # 9, 10, 11 (Fall)


def engineer_features(df):
    # ==========================================
    # 1. Financial Metrics
    # ==========================================
    df['profit'] = df['revenue'] - df['budget']
    df['ROI'] = np.where(df['budget'] > 0, df['revenue'] / df['budget'], 0)
    df['performance_status'] = np.where(df['revenue'] < df['budget'], 'Loss', 'Profit')

    # ==========================================
    # 2. Language & Company Grouping
    # ==========================================
    top_langs = df['original_language'].value_counts().nlargest(5).index
    df['language_group'] = df['original_language'].apply(lambda x: x if x in top_langs else 'Other')

    if 'production_companies' in df.columns:
        df['primary_company'] = df['production_companies'].apply(get_primary_company)
    else:
        df['primary_company'] = 'Unknown'

    # ==========================================
    # 3. Weighted Rating (Bayesian Formula)
    # ==========================================
    C = df['vote_average'].mean()
    m = df['vote_count'].quantile(0.60)
    df['weighted_rating'] = (
            (df['vote_count'] / (df['vote_count'] + m)) * df['vote_average'] +
            (m / (df['vote_count'] + m)) * C
    )

    # ==========================================
    # 4. Outlier Treatment (Capping)
    # ==========================================
    for col in ['popularity', 'runtime', 'ROI']:
        if col in df.columns:
            df = cap_outliers(df, col)

    # ==========================================
    # 5. Log Transformation & Scaling
    # ==========================================
    df['log_revenue'] = np.log1p(df['revenue'])
    df['log_budget'] = np.log1p(df['budget'])
    p_min, p_max = df['popularity'].min(), df['popularity'].max()
    df['popularity_score'] = ((df['popularity'] - p_min) / (p_max - p_min)) * 100

    # ==========================================
    # 6. Visualization & Temporal Features
    # ==========================================
    df['Decade'] = (df['release_year'] // 10) * 10
    df['Decade_Str'] = df['Decade'].astype(str) + 's'
    df['Season'] = df['release_month'].apply(get_season)

    bins = [-1, 10e6, 50e6, 150e6, float('inf')]  # Starts at -1 to capture any 0-budgets safely
    labels = ['Low (<10M)', 'Medium (10M-50M)', 'High (50M-150M)', 'Mega (>150M)']
    df['Budget_Tier'] = pd.cut(df['budget'], bins=bins, labels=labels)

    # Strict prompt requirement: High Rated if vote_average >= 7
    df['Rating_Cat'] = np.where(df['vote_average'] >= 7, 'High Rated', 'Low Rated')

    # ==========================================
    # 7. Strict Feature Selection (Final Dataset)
    # ==========================================
    base_cols = [
        'title', 'budget', 'revenue', 'profit', 'ROI', 'performance_status',
        'log_budget', 'log_revenue', 'release_year', 'release_month', 'release_day',
        'main_genre', 'runtime', 'vote_average', 'weighted_rating',
        'revenue_flag', 'language_group', 'popularity', 'popularity_score',
        'vote_count', 'primary_company', 'Decade', 'Decade_Str', 'Season',
        'Budget_Tier', 'Rating_Cat'
    ]

    # Automatically include dynamic genre one-hot columns (excluding the list array itself)
    genre_cols = [col for col in df.columns if col.startswith('genre_') and col != 'genre_list']
    final_cols = base_cols + genre_cols

    # Verify everything was successfully created
    missing = [c for c in final_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Pipeline Execution Failed. Missing columns during feature engineering: {missing}")

    return df[final_cols]