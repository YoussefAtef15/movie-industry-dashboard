## 🎬 Movie Industry Analytics Dashboard

![Dashboard Preview](https://img.shields.io/badge/UI-SaaS_Professional-blue?style=for-the-badge)
![Data Tool](https://img.shields.io/badge/Backend-Python_Pipeline-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Production_Ready-orange?style=for-the-badge)

## 📋 Project Overview
This project is a high-end, interactive analytics system designed to explore the global cinema industry's financial and qualitative trends. Built using **Python**, **Dash**, and **Plotly**, it leverages the **TMDB 5000 Movie Dataset** to provide stakeholders with data-driven insights into profitability, audience engagement, and production risks.

The system follows a strict **Data Engineering Architecture**, separating the heavy data processing (Backend Pipeline) from the interactive visualization (Frontend UI) to ensure a "Single Source of Truth."

---

## 🚀 Key Features

### 🧠 Backend Engine (Pipeline Architecture)
* **Single Source of Truth:** All complex metrics (ROI, Bayesian Weighted Rating, Profit) are pre-calculated in the backend strictly to ensure dashboard performance and data integrity.
* **Smart Imputation:** Automated genre-based logic to fill missing financial and duration data.
* **Outlier Mitigation:** Log transformations applied to financial data to handle blockbusters vs. indie films gracefully.

### 📊 Frontend SaaS-Style UI
* **Top Stats Cards:** Instant view of Total Movies, Total Profit, Average Rating, and Top Performing Genre.
* **Interactive Custom Explorer:** A powerful tool with **Smart Auto-Detection** that lets users build custom charts dynamically.
* **Modern Minimal Design:** Clean typography, soft slate borders, and a premium SaaS color palette.
* **Responsive Layout:** Mobile-friendly design that adapts from large monitors to handheld devices.

---

## 🛠 Tech Stack
* **Language:** Python 3.10+
* **Dashboard Framework:** Plotly Dash
* **Data Science Tools:** Pandas, NumPy, Scikit-learn
* **Styling:** CSS3 (SaaS Theme), HTML5
* **Development:** Jupyter Notebooks (for R&D)

---

## 📂 Project Structure
```text
movie_dashboard_project/
├── assets/                 # Custom CSS and static UI assets
│   └── style.css           # Premium SaaS styling rules
├── data/                   # Data storage (Raw and Preprocessed)
│   ├── raw_movies.csv      # Original Kaggle dataset
│   └── cleaned_movies.csv  # Final output from pipeline
├── notebooks/              # Research and Development
│   └── preprocessing.ipynb # Step-by-step EDA and pipeline drafting
├── src/                    # Core Backend Logic
│   ├── data_cleaning.py    # JSON parsing and initial cleaning
│   ├── feature_engineering.py # Dimension and metric creation
│   └── utils.py            # Dataset validation and pipeline management
├── app.py                  # Main Application (UI & Callbacks)
├── README.md               # Documentation
└── requirements.txt        # Project dependencies
```


## Instructions to Run

The application features a Smart Launch system. If the processed dataset is missing or corrupted, the dashboard will automatically trigger the backend pipeline to rebuild it before starting.

**1. Clone the project:**
```bash
git clone [https://github.com/YoussefAtef15/movie-industry-dashboard.git](https://github.com/YoussefAtef15/movie-industry-dashboard.git)
cd movie-industry-dashboard
```

**2. Download Data:**
```bash
Download the tmdb_5000_movies.csv from Kaggle and place it in the data/ folder as raw_movies.csv.
```

**3. Setup Virtual Environment:**
```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate

```

**5. Preprocess Data (Optional):**
Run all cells in `notebooks/preprocessing.ipynb` to generate `cleaned_movies.csv` (if not using the Smart Launch feature).

**6. Run the Dashboard:**
```bash
python app.py
```

Open your browser and navigate to: `http://127.0.0.1:8050/`

---

## 📊 Core Analytical Perspectives

The dashboard includes 13 professional visualizations:

* **Seasonal Profitability:** Finding the best release months.
* **Industry Titans:** Ranking production companies by total profit.
* **Risk Matrix:** Success vs. Failure rates across different budget tiers.
* **Genre Satisfaction:** Evaluating Reception Quality by genre.
* **Marketing Hype vs. Rating:** Correlating popularity scores with actual ratings.
* **Decade Trends:** Tracking production inflation and revenue growth over 40 years.
* **Runtime Optimization:** Identifying the "Sweet Spot" duration for high ratings.
