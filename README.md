# Movie Industry Analysis Dashboard 🎬

## Project Overview
This project is an interactive web dashboard built with Plotly Dash. It analyzes the **TMDB 5000 Movie Dataset** to uncover trends in the movie industry, including financial performance (budgets vs. revenues), genre popularity, and rating distributions over time. 

This project fulfills all requirements for the Data Visualization course, demonstrating the ability to extract insights from raw data using 13 distinct chart types and interactive filtering components.

## Features
* **Data Processing:** Cleaned JSON-like strings in the dataset and engineered new features (Profit, ROI, and Release Year).
* **Interactive Filters:** Filter data dynamically by Genre, Year Range, and Original Language.
* **13 Distinct Chart Types:** Includes Bar, Column, Stacked, Clustered, Scatter, Bubble, Histogram, Box, Violin, Line, and Area charts.
* **Responsive Layout:** Clean CSS grid design viewable on standard screens without horizontal scrolling.

## Dataset Description
- **Name:** TMDB 5000 Movie Dataset
- **Source:** [Kaggle](https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata)
- **Content:** Information on ~5,000 movies including budgets, revenues, release dates, genres, and ratings.


## Instructions to Run

1.  **Clone or setup the project structure:** Ensure your files match the structure mentioned in the codebase.
2.  **Download Data:** Download the `tmdb_5000_movies.csv` from Kaggle and place it in the `data/` folder as `raw_movies.csv`.
3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Preprocess Data:** Run all cells in `notebooks/preprocessing.ipynb` to generate `cleaned_movies.csv`.
5.  **Run the App:**
    ```bash
    python app.py
    ```
6.  **View Dashboard:** Open your browser and navigate to `http://127.0.0.1:8050/`.