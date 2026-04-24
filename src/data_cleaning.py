import pandas as pd
import numpy as np
import ast


def clean_data(df):
    # ==========================================
    # 1. Date Handling & Corrupt Rows Removal
    # ==========================================
    df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
    df['release_year'] = df['release_date'].dt.year.astype('Int64')
    df['release_month'] = df['release_date'].dt.month.astype('Int64')
    df['release_day'] = df['release_date'].dt.day.astype('Int64')

    # Drop critically corrupted rows
    df = df.dropna(subset=['runtime', 'release_date'])

    # ==========================================
    # 2. Genre Extraction & Multi-Label One-Hot Encoding
    # ==========================================
    def extract_all_genres(text):
        try:
            genres = [i['name'] for i in ast.literal_eval(text)]
            return genres if genres else ['Unknown']
        except:
            return ['Unknown']

    df['genre_list'] = df['genres'].apply(extract_all_genres)

    # Extract main genre for simple categorizations
    df['main_genre'] = df['genre_list'].apply(lambda x: x[0] if len(x) > 0 else 'Unknown')

    # Create dynamic binary columns for each genre
    all_unique_genres = set([genre for sublist in df['genre_list'] for genre in sublist])
    for genre in all_unique_genres:
        df[f'genre_{genre}'] = df['genre_list'].apply(lambda x: 1 if genre in x else 0)

    # ==========================================
    # 3. Helper Function: Multi-Genre Imputation
    # ==========================================
    def multi_genre_impute(dataframe, target_col, agg_method='median'):
        temp_df = dataframe.copy()
        genre_aggs = {}
        for genre in all_unique_genres:
            genre_mask = temp_df[f'genre_{genre}'] == 1
            if agg_method == 'median':
                genre_aggs[genre] = temp_df.loc[genre_mask, target_col].median()
            else:
                genre_aggs[genre] = temp_df.loc[genre_mask, target_col].mean()

        def calculate_imputation_value(movie_genres):
            valid_aggs = [genre_aggs[g] for g in movie_genres if pd.notna(genre_aggs.get(g))]
            return np.mean(valid_aggs) if valid_aggs else np.nan

        missing_mask = temp_df[target_col].isna() | (temp_df[target_col] == 0)
        temp_df.loc[missing_mask, target_col] = temp_df.loc[missing_mask, 'genre_list'].apply(
            calculate_imputation_value)

        global_agg = temp_df[target_col].median() if agg_method == 'median' else temp_df[target_col].mean()
        return temp_df[target_col].fillna(global_agg)

    # ==========================================
    # 4. Impute Missing Values (Budget & Runtime)
    # ==========================================
    df['budget'] = df['budget'].replace(0, np.nan)
    df['runtime'] = df['runtime'].replace(0, np.nan)

    df['budget'] = multi_genre_impute(df, target_col='budget', agg_method='median')
    df['runtime'] = multi_genre_impute(df, target_col='runtime', agg_method='median')

    # ==========================================
    # 5. Clean Ratings & Impute
    # ==========================================
    df.loc[df['vote_count'] == 0, 'vote_average'] = np.nan
    df.loc[(df['vote_count'] > 0) & (df['vote_average'] == 0), 'vote_average'] = np.nan
    df['vote_average'] = multi_genre_impute(df, target_col='vote_average', agg_method='mean')

    # ==========================================
    # 6. Revenue Flagging & Smart Imputation
    # ==========================================
    pop_median = df['popularity'].median()
    df['revenue_flag'] = 'valid'

    df.loc[
        (df['revenue'] == 0) & (df['vote_count'] > 100) & (df['popularity'] > pop_median), 'revenue_flag'] = 'missing'
    df.loc[(df['revenue'] == 0) & (df['vote_count'] <= 100), 'revenue_flag'] = 'possible_flop'

    # Impute ONLY the missing ones
    df.loc[df['revenue_flag'] == 'missing', 'revenue'] = np.nan
    df['revenue'] = multi_genre_impute(df, target_col='revenue', agg_method='median')
    df['revenue'] = df['revenue'].fillna(0)  # Keep possible flops as 0

    # ==========================================
    # 7. Drop Useless Columns
    # ==========================================
    cols_to_drop = ['homepage', 'overview', 'tagline', 'original_title', 'id', 'status', 'keywords', 'genres',
                    'genre_list']
    df = df.drop(columns=[col for col in cols_to_drop if col in df.columns], errors='ignore')

    return df