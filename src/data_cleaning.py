import pandas as pd
import ast


def clean_data(df):
    # Drop rows with missing essential data
    df = df.dropna(subset=['release_date', 'title'])

    # Remove duplicates
    df = df.drop_duplicates()

    # Function to extract the first genre from the JSON-like string
    def extract_main_genre(genre_str):
        try:
            # Safely evaluate the string into a list of dictionaries
            genres = ast.literal_eval(genre_str)
            if len(genres) > 0:
                return genres[0]['name']
            return 'Unknown'
        except:
            return 'Unknown'

    # Apply extraction
    df['main_genre'] = df['genres'].apply(extract_main_genre)

    return df