import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import calendar
import os

try:
    from src.utils import validate_dataset, process_pipeline
except ImportError:
    pass

# ==========================================
# 1. DATA PIPELINE & LOADING
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DATA_PATH = os.path.join(BASE_DIR, 'data', 'raw_movies.csv')
CLEAN_DATA_PATH = os.path.join(BASE_DIR, 'data', 'cleaned_movies.csv')

# Ensure clean data exists
if not os.path.exists(CLEAN_DATA_PATH):
    print("\n[INFO] Clean dataset missing. Auto-building pipeline from raw data...")
    if not os.path.exists(RAW_DATA_PATH):
        raise FileNotFoundError(f"Raw data missing at {RAW_DATA_PATH}")
    process_pipeline(RAW_DATA_PATH, CLEAN_DATA_PATH)
    print("[INFO] Pipeline complete. Starting dashboard...\n")

df = pd.read_csv(CLEAN_DATA_PATH)

try:
    validate_dataset(df)
except NameError:
    pass

# Compute derived columns safely
if 'Decade' not in df.columns:
    df['Decade'] = (df['release_year'] // 10) * 10
    df['Decade_Str'] = df['Decade'].astype(str) + 's'


def get_season(month):
    if pd.isna(month): return 'Unknown'
    month = int(month)
    if month in [12, 1, 2]:
        return 'Winter'
    elif month in [3, 4, 5]:
        return 'Spring'
    elif month in [6, 7, 8]:
        return 'Summer'
    else:
        return 'Autumn'


if 'Season' not in df.columns and 'release_month' in df.columns:
    df['Season'] = df['release_month'].apply(get_season)

if 'Budget_Tier' not in df.columns and 'budget' in df.columns:
    bins = [0, 10e6, 50e6, 150e6, float('inf')]
    labels = ['Low (<10M)', 'Medium (10M-50M)', 'High (50M-150M)', 'Mega (>150M)']
    df['Budget_Tier'] = pd.cut(df['budget'], bins=bins, labels=labels)

if 'Rating_Cat' not in df.columns and 'weighted_rating' in df.columns:
    median_rating = df['weighted_rating'].median()
    df['Rating_Cat'] = np.where(df['weighted_rating'] >= median_rating, 'High Rated', 'Low Rated')

# Dashboard Filter Variables
top_genres = df['main_genre'].value_counts().nlargest(5).index.tolist() if 'main_genre' in df.columns else []
available_languages = df['language_group'].dropna().unique().tolist() if 'language_group' in df.columns else []
min_year = int(df['release_year'].min()) if 'release_year' in df.columns else 1980
max_year = int(df['release_year'].max()) if 'release_year' in df.columns else 2023

df = df[df['main_genre'].isin(top_genres)]

# Data types for custom explorer
NUMERICAL_COLS = [
    'budget', 'revenue', 'profit', 'ROI', 'log_budget', 'log_revenue',
    'runtime', 'vote_average', 'weighted_rating', 'popularity', 'popularity_score', 'vote_count'
]
CATEGORICAL_COLS = [
    'main_genre', 'performance_status', 'revenue_flag', 'language_group',
    'release_year', 'Season', 'Budget_Tier', 'Rating_Cat', 'Decade_Str', 'primary_company'
]

# Standardized Color Palette
COLOR_PRIMARY = '#2563EB'
COLOR_SUCCESS = '#16A34A'
COLOR_DANGER = '#DC2626'
COLOR_SECONDARY = '#64748B'
COLOR_BORDER = '#CBD5E1'
GUIDELINE_COLORS = ['#2563EB', '#3B82F6', '#60A5FA', '#93C5FD', '#1D4ED8', '#1E40AF', '#1E3A8A']

# ==========================================
# 2. DASHBOARD APP INITIALIZATION
# ==========================================
app = dash.Dash(__name__, assets_ignore='.*~')
app.title = "Movie Analytics"


def create_chart_card(chart_id, title, relation, insight, full_width=False):
    """HTML Structure for each individual chart card."""
    className = 'chart-card span-full' if full_width else 'chart-card'
    return html.Div(className=className, children=[
        html.H3(title, className='chart-header'),
        html.P([html.B("Relationship: "), relation],
               style={'fontSize': '0.85rem', 'color': '#64748B', 'marginBottom': '15px', 'paddingBottom': '15px',
                      'borderBottom': '1px solid #E2E8F0'}),
        dcc.Graph(id=chart_id),
        html.Div(style={'backgroundColor': '#F8FAFC', 'padding': '15px', 'borderLeft': '3px solid #2563EB',
                        'marginTop': '20px', 'borderRadius': '0 8px 8px 0'}, children=[
            html.P(html.B("Insight: "), style={'margin': '0 0 5px 0', 'color': '#1E40AF', 'fontSize': '0.85rem'}),
            html.P(insight, style={'margin': '0', 'fontSize': '0.85rem', 'color': '#475569', 'lineHeight': '1.6'})
        ])
    ])


# ==========================================
# 3. DASHBOARD UI LAYOUT
# ==========================================
app.layout = html.Div(className='app-container', children=[

    # Left Sidebar
    html.Div(className='sidebar', children=[
        html.Div(className='sidebar-header', children=[
            html.Div(className='profile-pic', children="MA"),
            html.H2("Movie Analytics", className='profile-name'),
            html.P("Performance Dashboard", className='profile-role')
        ]),
        html.Hr(className='sidebar-divider'),
        html.H3("FILTERS", className='nav-title'),

        html.Div(className='sidebar-filters', children=[
            html.Div(className='filter-group', children=[
                html.Label("Select Genres", className='filter-label'),
                dcc.Dropdown(
                    id='genre-filter', options=[{'label': genre, 'value': genre} for genre in top_genres],
                    value=top_genres, multi=True, className='custom-dropdown'
                )
            ]),
            html.Div(className='filter-group', children=[
                html.Label("Select Language", className='filter-label'),
                dcc.Dropdown(
                    id='language-filter', options=[{'label': lang, 'value': lang} for lang in available_languages],
                    value=available_languages, multi=True, className='custom-dropdown'
                )
            ]),
            html.Div(className='filter-group', children=[
                html.Label("Release Year", className='filter-label'),
                html.Div(style={'padding': '10px 5px 30px 5px'}, children=[
                    dcc.RangeSlider(
                        id='year-filter', min=min_year, max=max_year, step=1,
                        marks={min_year: str(min_year), 1980: '1980', 2000: '2000', max_year: str(max_year)},
                        value=[1980, max_year], tooltip={"placement": "bottom", "always_visible": True}
                    )
                ])
            ])
        ])
    ]),

    # Main Viewing Area
    html.Div(className='main-content', children=[
        html.Div(className='top-header', children=[
            html.H1("Overview", className='page-title')
        ]),

        html.Div(className='top-stats-grid', children=[
            html.Div(className='stat-card', children=[
                html.P("Total Movies", className='stat-title', title="Total number of movies in the selected filters."),
                html.H3(id='stat-total-movies', className='stat-value')
            ]),
            html.Div(className='stat-card', children=[
                html.P("Estimated Margin", className='stat-title',
                       title="Estimated Box Office Margin (Revenue - 2x Budget). Includes statistically imputed values."),
                html.H3(id='stat-total-profit', className='stat-value')
            ]),
            html.Div(className='stat-card', children=[
                html.P("Average Rating", className='stat-title',
                       title="Average Bayesian weighted rating for the selected movies."),
                html.H3(id='stat-avg-rating', className='stat-value')
            ]),
            html.Div(className='stat-card', children=[
                html.P("Top Genre", className='stat-title',
                       title="Most frequent primary genre in the selected filters."),
                html.H3(id='stat-top-genre', className='stat-value')
            ]),
        ]),

        html.Div(className='charts-grid', children=[
            create_chart_card('chart-1', "1. Column Chart: Seasonal Impact on Movie Profitability",
                              "Month vs Avg Profit",
                              "Peak summer months and holidays show a massive spike in profitability.", False),
            create_chart_card('chart-2', "2. Horizontal Bar Chart: Industry Titans by Total Profit",
                              "Total Profit vs Company", "Confirms market concentration at the top studios.", False),
            create_chart_card('chart-3', "3. Stacked Bar Chart: Profit vs. Loss Composition by Budget Tier",
                              "Budget Tier vs Composition (%)",
                              "The Medium Budget tier is proportionally the riskiest investment.", False),
            create_chart_card('chart-4', "4. Stacked Bar Chart: Audience Satisfaction Composition by Genre",
                              "Volume vs Genre",
                              "Drama is the gold standard for quality. Comedy suffers from market saturation.", False),
            create_chart_card('chart-5', "5. Clustered Column Chart: Audience Rating vs. Marketing Hype",
                              "Month vs Normalized Score",
                              "Audience Ratings remain relatively flat, showing studios control hype, not reception.",
                              False),
            create_chart_card('chart-6', "6. Clustered Bar Chart: Average Budget vs. Profit by Decade",
                              "Amount vs Decade",
                              "Average net profit has remained resilient despite rising production budgets.", False),
            create_chart_card('chart-7', "7. Scatter Plot: Runtime vs. Audience Rating", "Runtime vs Rating",
                              "Vast majority of successful films congregate within the 80-120-minute window.", False),
            create_chart_card('chart-8', "8. Bubble Chart: Audience Engagement vs. Profitability",
                              "Votes vs Profit (Size: Budget)",
                              "Higher audience engagement correlates with higher profitability.", False),
            create_chart_card('chart-9', "9. Histogram: Distribution of Movie Runtime (Industry Standard)",
                              "Minutes vs Frequency",
                              "The 90-120 minute window is the optimal 'Sweet Spot' for theatrical distribution.",
                              True),
            create_chart_card('chart-10', "10. Box Plot: ROI Distribution by Season (Volatility Comparison)",
                              "Season vs ROI Multiplier",
                              "Summer releases exhibit higher median ROI but greater variability.", False),
            create_chart_card('chart-11', "11. Violin Plot: Log Budget Distribution by Performance Status",
                              "Status vs Density (Log Budget)",
                              "High budgets are not a guarantee of safety; they guarantee exposure.", False),
            create_chart_card('chart-12', "12. Time-Series Analysis: Average Budget vs. Revenue Trends (1990-2017)",
                              "Year vs Amount", "Revenue remains highly volatile, confirming a hit-driven industry.",
                              True),
            create_chart_card('chart-13', "13. Area Chart: Genre Contribution to Total Profit Over Time",
                              "Year vs Cumulative Profit",
                              "Action and Adventure dominate total profit growth post-2010.", True),
        ]),

        # Custom Explorer
        html.Div(className='custom-explorer', children=[
            html.Div(className='custom-explorer-header', children=[
                html.H2("Interactive Custom Explorer"),
                html.P(
                    "Dynamically build visualizations. Choose from the 13 available chart types and select any variables.")
            ]),
            html.Div(className='explorer-controls', children=[
                html.Div(className='explorer-control-item', children=[
                    html.Label("Chart Type", className='filter-label-dark'),
                    dcc.Dropdown(
                        id='custom-chart-type',
                        options=[
                            {'label': 'Auto Mode', 'value': 'auto'},
                            {'label': '1. Column Chart', 'value': 'column'},
                            {'label': '2. Horizontal Bar Chart', 'value': 'bar'},
                            {'label': '3. Stacked Bar Chart', 'value': 'stacked_bar'},
                            {'label': '4. Stacked Column Chart', 'value': 'stacked_column'},
                            {'label': '5. Clustered Column Chart', 'value': 'clustered_column'},
                            {'label': '6. Clustered Bar Chart', 'value': 'clustered_bar'},
                            {'label': '7. Scatter Plot', 'value': 'scatter'},
                            {'label': '8. Bubble Chart', 'value': 'bubble'},
                            {'label': '9. Histogram', 'value': 'histogram'},
                            {'label': '10. Box Plot', 'value': 'box'},
                            {'label': '11. Violin Plot', 'value': 'violin'},
                            {'label': '12. Line Chart (Time-Series)', 'value': 'line'},
                            {'label': '13. Area Chart', 'value': 'area'}
                        ],
                        value='auto', clearable=False, className='custom-dropdown'
                    )
                ]),
                html.Div(className='explorer-control-item', id='custom-x-axis-container', children=[
                    html.Label("X-Axis", id='x-axis-label', className='filter-label-dark'),
                    dcc.Dropdown(id='custom-x-axis', clearable=False, className='custom-dropdown')
                ]),
                html.Div(className='explorer-control-item', id='custom-y-axis-container', children=[
                    html.Label("Y-Axis", id='y-axis-label', className='filter-label-dark'),
                    dcc.Dropdown(id='custom-y-axis', clearable=False, className='custom-dropdown')
                ]),
                html.Div(className='explorer-control-item', id='custom-group-axis-container', children=[
                    html.Label("Color / Group", id='group-axis-label', className='filter-label-dark'),
                    dcc.Dropdown(id='custom-group-axis', clearable=False, className='custom-dropdown')
                ]),
                html.Div(className='explorer-control-item', id='custom-size-axis-container', children=[
                    html.Label("Size (Bubble)", id='size-axis-label', className='filter-label-dark'),
                    dcc.Dropdown(id='custom-size-axis', clearable=False, className='custom-dropdown')
                ]),
                # NEW TOP N FILTER
                html.Div(className='explorer-control-item', children=[
                    html.Label("Top N Filter", className='filter-label-dark'),
                    dcc.Dropdown(
                        id='custom-top-n',
                        options=[
                            {'label': 'Top 5', 'value': 5},
                            {'label': 'Top 10', 'value': 10},
                            {'label': 'Top 15', 'value': 15},
                            {'label': 'Top 20', 'value': 20},
                            {'label': 'Show All', 'value': 0}
                        ],
                        value=15, clearable=False, className='custom-dropdown'
                    )
                ])
            ]),
            html.H3(id='custom-chart-title', className='chart-header',
                    style={'marginTop': '30px', 'textAlign': 'center'}),
            dcc.Graph(id='custom-graph-output')
        ]),

        html.Div(className='project-info', children=[
            html.H3("About This Project", className='project-title'),
            html.P(
                "This dashboard provides a comprehensive analysis of the motion picture industry, exploring trends in profitability, genre performance, and audience engagement over several decades.",
                className='project-desc'),
            html.Div(className='project-links', children=[
                html.A("Dataset (Kaggle)", href="https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata",
                       target="_blank", className='project-link'),
                html.Span(" | ", className='link-separator'),
                html.A("GitHub Repository", href="https://github.com/YoussefAtef15/movie-industry-dashboard",
                       target="_blank", className='project-link')
            ]),
            html.P(
                "Disclaimer: Financial figures use the Hollywood '2x Budget' rule for realistic profitability. "
                "Furthermore, missing budgets and revenues were statistically imputed based on genre medians to preserve data distribution.",
                style={'fontSize': '0.85rem', 'color': '#DC2626', 'maxWidth': '700px', 'margin': '0 auto 20px auto',
                       'textAlign': 'center', 'fontWeight': '500'}
            )
        ])
    ])
])


# ==========================================
# 4. CHART BUILDING HELPERS
# ==========================================
def apply_standard_layout(fig, title_text, xaxis_title, yaxis_title, legend_title="Legend",
                          barmode=None, bargap=None, bargroupgap=None, xaxis_range=None, yaxis_range=None,
                          xaxis_tickangle=None, yaxis_ticksuffix=None, yaxis_rangemode=None,
                          xaxis_rangemode=None, xaxis_categoryorder=None, xaxis_categoryarray=None,
                          margin_l=60, margin_r=180):
    """
    100% Bulletproof function for ALL Plotly versions.
    Enforces Top-Right Legend positioning strictly outside the plot area.
    Fixes unexpected keyword arguments.
    """

    safe_title = f"<b>{title_text}</b>" if title_text else ""
    safe_xaxis = f"<b>{xaxis_title}</b>" if xaxis_title else ""
    safe_yaxis = f"<b>{yaxis_title}</b>" if yaxis_title else ""
    safe_legend = f"<b>{legend_title}</b>" if legend_title else ""

    # 1. Base Layout Update (Legend Top Right, Outside Plot)
    fig.update_layout(
        plot_bgcolor='#FFFFFF',
        paper_bgcolor='#FFFFFF',
        font=dict(color='#334155', family='Inter', size=12),
        margin=dict(t=80, b=60, l=margin_l, r=margin_r),  # Increased right margin ensures legend fits perfectly
        title=dict(
            text=safe_title,
            x=0.5,
            y=0.95,
            font=dict(size=16, color='#0F172A', family='Inter')
        ),
        legend=dict(
            title=dict(text=safe_legend, font=dict(size=12, color='#0F172A', family='Inter')),
            bgcolor='rgba(255, 255, 255, 0.9)',
            bordercolor='#CBD5E1',
            borderwidth=1,
            font=dict(size=11, color='#475569'),
            yanchor="top", y=1,
            xanchor="left", x=1.02,  # Pushes legend strictly outside to the right
            orientation="v"
        ),
        showlegend=True
    )

    # 2. X-Axis Safely Updated
    fig.update_xaxes(
        title=dict(text=safe_xaxis, font=dict(size=13, color='#1E293B', family='Inter')),
        color='#64748B', showline=True, linecolor='#CBD5E1',
        linewidth=1, mirror=False, gridcolor='#F1F5F9', zerolinecolor='#E2E8F0'
    )

    # 3. Y-Axis Safely Updated
    fig.update_yaxes(
        title=dict(text=safe_yaxis, font=dict(size=13, color='#1E293B', family='Inter')),
        color='#64748B', showline=True, linecolor='#CBD5E1',
        linewidth=1, mirror=False, gridcolor='#F1F5F9', zerolinecolor='#E2E8F0'
    )

    # 4. Optional Logic
    if barmode: fig.update_layout(barmode=barmode)
    if bargap: fig.update_layout(bargap=bargap)
    if bargroupgap: fig.update_layout(bargroupgap=bargroupgap)

    if xaxis_range: fig.update_xaxes(range=xaxis_range)
    if yaxis_range: fig.update_yaxes(range=yaxis_range)
    if xaxis_tickangle is not None: fig.update_xaxes(tickangle=xaxis_tickangle)
    if yaxis_ticksuffix: fig.update_yaxes(ticksuffix=yaxis_ticksuffix)
    if yaxis_rangemode: fig.update_yaxes(rangemode=yaxis_rangemode)
    if xaxis_rangemode: fig.update_xaxes(rangemode=xaxis_rangemode)
    if xaxis_categoryorder: fig.update_xaxes(categoryorder=xaxis_categoryorder)
    if xaxis_categoryarray: fig.update_xaxes(categoryarray=xaxis_categoryarray)

    return fig


def get_empty_state(message):
    """Returns a clean empty state graphic."""
    fig = go.Figure()
    fig.add_annotation(text=f"<b>{message}</b>", x=0.5, y=0.5, showarrow=False, font=dict(color="#64748B", size=14))
    fig.update_layout(plot_bgcolor='#FFFFFF', paper_bgcolor='#FFFFFF', xaxis=dict(visible=False),
                      yaxis=dict(visible=False))
    return fig


# --- SMART DYNAMIC CHART BUILDER ---
def build_dynamic_chart(df_filtered, chart_type, x_col, y_col, group_col, size_col, top_n):
    if not x_col or x_col == 'None':
        return apply_standard_layout(get_empty_state("Select an X-Axis to begin exploration"),
                                     "Select X-Axis", "", ""), "Interactive Explorer Output"

    y_col = None if y_col == 'None' else y_col
    group_col = None if group_col == 'None' else group_col
    size_col = None if size_col == 'None' else size_col

    x_is_num = x_col in NUMERICAL_COLS
    y_is_num = y_col in NUMERICAL_COLS if y_col else False
    x_is_cat = x_col in CATEGORICAL_COLS
    y_is_cat = y_col in CATEGORICAL_COLS if y_col else False

    # Auto-Detection Logic
    if chart_type == 'auto':
        if x_is_num and not y_col:
            chart_type = 'histogram'
        elif x_is_num and y_is_num:
            chart_type = 'bubble' if size_col else 'scatter'
        elif (x_is_cat and y_is_num) or (x_is_num and y_is_cat) or (x_is_cat and not y_col):
            chart_type = 'column'
        elif x_is_cat and y_is_cat:
            chart_type = 'stacked_column'
        else:
            chart_type = 'scatter'

    # Strict Validation with specific messages
    error_msg = None
    if chart_type in ['scatter', 'bubble'] and (not x_is_num or not y_is_num):
        error_msg = f"{chart_type.replace('_', ' ').title()} plots require both X and Y to be Numerical."
    elif chart_type == 'bubble' and not size_col:
        error_msg = "Bubble charts require a Size variable."
    elif chart_type == 'histogram' and not x_is_num:
        error_msg = "Histograms require X to be Numerical."
    elif chart_type in ['line', 'area'] and not y_col:
        error_msg = f"{chart_type.replace('_', ' ').title()} charts require a Y-Axis."

    if error_msg:
        fig = go.Figure()
        fig.add_annotation(text=f"<b>{error_msg}</b>", x=0.5, y=0.5, showarrow=False,
                           font=dict(color=COLOR_DANGER, size=14))
        fig.update_layout(plot_bgcolor='#FEF2F2', paper_bgcolor='#FFFFFF', xaxis=dict(visible=False),
                          yaxis=dict(visible=False))
        return apply_standard_layout(fig, "Configuration Error", "", ""), "Configuration Error"

    # --- CLUTTER FIX: Dynamic Top N Filter ---
    if top_n > 0:
        if x_is_cat and x_col not in ['None', None]:
            top_x = df_filtered[x_col].value_counts().nlargest(top_n).index
            df_filtered = df_filtered[df_filtered[x_col].isin(top_x)]

        if y_is_cat and y_col not in ['None', None]:
            top_y = df_filtered[y_col].value_counts().nlargest(top_n).index
            df_filtered = df_filtered[df_filtered[y_col].isin(top_y)]

        if group_col and group_col not in ['None', None] and group_col in CATEGORICAL_COLS:
            top_g = df_filtered[group_col].value_counts().nlargest(top_n).index
            df_filtered = df_filtered[df_filtered[group_col].isin(top_g)]

    # Build the Chart dynamically
    fig = go.Figure()
    is_count_based = False
    if chart_type in ['column', 'stacked_column', 'clustered_column', 'bar', 'stacked_bar', 'clustered_bar']:
        if (x_is_cat and not y_col) or (x_is_cat and y_is_cat):
            is_count_based = True

    groups = [None] if not group_col else df_filtered[group_col].dropna().unique()

    for i, g in enumerate(groups):
        df_g = df_filtered if g is None else df_filtered[df_filtered[group_col] == g]
        trace_name = str(g) if g is not None else (y_col.replace('_', ' ').title() if y_col else "Count")
        c_val = GUIDELINE_COLORS[i % len(GUIDELINE_COLORS)]

        if chart_type == 'scatter':
            fig.add_trace(go.Scatter(x=df_g[x_col], y=df_g[y_col], mode='markers', name=trace_name,
                                     marker=dict(color=c_val, size=7, opacity=0.7,
                                                 line=dict(color='#FFFFFF', width=0.5)), text=df_g['title']))

        elif chart_type == 'bubble':
            sizeref = 2.0 * (df_filtered[size_col].max() or 1) / (35 ** 2)
            fig.add_trace(go.Scatter(x=df_g[x_col], y=df_g[y_col], mode='markers', name=trace_name,
                                     marker=dict(color=c_val, size=df_g[size_col], sizeref=sizeref, sizemode='area',
                                                 opacity=0.6, line=dict(color='#FFFFFF', width=0.5)),
                                     text=df_g['title']))

        elif chart_type == 'histogram':
            fig.add_trace(
                go.Histogram(x=df_g[x_col], name=trace_name, marker_color=c_val, opacity=0.8, marker_line_width=0))

        elif chart_type in ['column', 'stacked_column', 'clustered_column']:
            if is_count_based:
                val_counts = df_g[x_col].value_counts().reset_index()
                val_counts.columns = [x_col, 'Count']
                fig.add_trace(go.Bar(x=val_counts[x_col], y=val_counts['Count'], name=trace_name, marker_color=c_val,
                                     marker_line_width=0, text=val_counts['Count'], textposition='outside',
                                     textfont=dict(color='black', family='Inter')))
            else:
                calc_x = x_col if x_is_cat else y_col
                calc_y = y_col if x_is_cat else x_col
                agg = df_g.groupby(calc_x)[calc_y].mean().reset_index().sort_values(by=calc_y, ascending=False)
                # Ensure numerical formatting
                text_vals = agg[calc_y].apply(lambda v: f"{v / 1e6:.1f}M" if v > 1e6 else f"{v:.1f}")
                fig.add_trace(
                    go.Bar(x=agg[calc_x], y=agg[calc_y], name=trace_name, marker_color=c_val, marker_line_width=0,
                           text="<b>" + text_vals + "</b>", textposition='outside',
                           textfont=dict(color='black', family='Inter')))

        elif chart_type in ['bar', 'stacked_bar', 'clustered_bar']:
            if is_count_based:
                val_counts = df_g[x_col].value_counts().reset_index()
                val_counts.columns = [x_col, 'Count']
                fig.add_trace(go.Bar(y=val_counts[x_col], x=val_counts['Count'], orientation='h', name=trace_name,
                                     marker_color=c_val, marker_line_width=0, text=val_counts['Count'],
                                     textposition='outside',
                                     textfont=dict(color='black', family='Inter')))
            else:
                calc_x = x_col if x_is_num else y_col
                calc_y = y_col if x_is_num else x_col
                agg = df_g.groupby(calc_y)[calc_x].mean().reset_index().sort_values(by=calc_x, ascending=True)
                # Ensure numerical formatting
                text_vals = agg[calc_x].apply(lambda v: f"{v / 1e6:.1f}M" if v > 1e6 else f"{v:.1f}")
                fig.add_trace(go.Bar(y=agg[calc_y], x=agg[calc_x], orientation='h', name=trace_name, marker_color=c_val,
                                     marker_line_width=0, text="<b>" + text_vals + "</b>", textposition='outside',
                                     textfont=dict(color='black', family='Inter')))

        elif chart_type == 'box':
            if x_is_cat:
                fig.add_trace(
                    go.Box(x=df_g[x_col], y=df_g[y_col] if y_col else df_g[NUMERICAL_COLS[0]], name=trace_name,
                           marker_color=c_val, line_width=1))
            else:
                fig.add_trace(go.Box(x=df_g[x_col], y=df_g[y_col] if y_col else None, orientation='h', name=trace_name,
                                     marker_color=c_val, line_width=1))

        elif chart_type == 'violin':
            # Custom colors for Profit and Loss to match guidelines
            if str(g) == 'Profit':
                v_color = '#A9D18E'
            elif str(g) == 'Loss':
                v_color = '#FF6666'
            else:
                v_color = c_val

            if x_is_cat:
                y_target = y_col if y_col else NUMERICAL_COLS[0]
                fig.add_trace(
                    go.Violin(x=df_g[x_col], y=df_g[y_target], name=trace_name,
                              line_color='black', fillcolor=v_color,
                              box_visible=True, opacity=0.9))

                # Add median annotations dynamically
                for x_cat in df_g[x_col].dropna().unique():
                    subset = df_g[df_g[x_col] == x_cat]
                    if not subset.empty:
                        median_val = subset[y_target].median()
                        if pd.notna(median_val):
                            fig.add_annotation(
                                x=x_cat,
                                y=median_val,
                                text=f"<b>{median_val:.2f}</b>",
                                showarrow=False,
                                xshift=45,
                                font=dict(color='black', size=12, family="Arial")
                            )
            else:
                y_target = y_col if y_col else CATEGORICAL_COLS[0]
                fig.add_trace(
                    go.Violin(x=df_g[x_col], y=df_g[y_target] if y_col else None, orientation='h', name=trace_name,
                              line_color='black', fillcolor=v_color,
                              box_visible=True, opacity=0.9))

                # Add median annotations for horizontal violins
                if y_col and y_is_cat:
                    for y_cat in df_g[y_col].dropna().unique():
                        subset = df_g[df_g[y_col] == y_cat]
                        if not subset.empty:
                            median_val = subset[x_col].median()
                            if pd.notna(median_val):
                                fig.add_annotation(
                                    x=median_val,
                                    y=y_cat,
                                    text=f"<b>{median_val:.2f}</b>",
                                    showarrow=False,
                                    yshift=20,
                                    font=dict(color='black', size=12, family="Arial")
                                )

        elif chart_type == 'line':
            agg = df_g.groupby(x_col)[y_col].mean().reset_index()
            fig.add_trace(go.Scatter(x=agg[x_col], y=agg[y_col], mode='lines+markers', name=trace_name,
                                     line=dict(color=c_val, width=2)))

        elif chart_type == 'area':
            agg = df_g.groupby(x_col)[y_col].sum().reset_index()
            fig.add_trace(
                go.Scatter(x=agg[x_col], y=agg[y_col], mode='lines', stackgroup='one', name=trace_name, fillcolor=c_val,
                           line_width=0))

    barmode_str = None
    if chart_type in ['stacked_column', 'stacked_bar']:
        barmode_str = 'stack'
    elif chart_type in ['clustered_column', 'clustered_bar']:
        barmode_str = 'group'
    elif chart_type == 'histogram':
        barmode_str = 'overlay'

    y_label = y_col.replace('_', ' ').title() if y_col else ("Count" if is_count_based else "")
    x_label = x_col.replace('_', ' ').title()

    if chart_type in ['bar', 'stacked_bar', 'clustered_bar'] and not is_count_based:
        if x_is_num:
            y_label, x_label = x_label, y_col.replace('_', ' ').title()

    title_text = f"{y_label} vs {x_label}" if y_label else f"Distribution of {x_label}"
    legend_text = group_col.replace('_', ' ').title() if group_col and group_col != 'None' else "Legend"
    margin_l_val = 150 if chart_type in ['bar', 'stacked_bar', 'clustered_bar'] else 60

    # Expand axis slightly to accommodate the new text labels
    x_range = None
    y_range = None
    if chart_type in ['bar', 'stacked_bar', 'clustered_bar'] and not is_count_based:
        max_val = df_filtered.groupby(y_col if x_is_num else x_col)[x_col if x_is_num else y_col].mean().max()
        x_range = [0, max_val * 1.15]
    elif chart_type in ['column', 'stacked_column', 'clustered_column'] and not is_count_based:
        max_val = df_filtered.groupby(x_col if x_is_cat else y_col)[y_col if x_is_cat else x_col].mean().max()
        y_range = [0, max_val * 1.15]

    fig = apply_standard_layout(
        fig,
        title_text=title_text,
        xaxis_title=x_label,
        yaxis_title=y_label,
        legend_title=legend_text,
        barmode=barmode_str,
        margin_l=margin_l_val,
        margin_r=180,
        xaxis_range=x_range,
        yaxis_range=y_range,
        yaxis_rangemode="tozero" if chart_type in ['column', 'clustered_column'] else None,
        xaxis_rangemode="tozero" if chart_type in ['bar', 'clustered_bar'] else None
    )

    # Apply specific styling to match the Violin plot guideline
    if chart_type == 'violin':
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(color='black', showgrid=False, showline=True, linecolor='gray', linewidth=1.5, mirror=True),
            yaxis=dict(color='black', showgrid=True, gridcolor='gray', griddash='dash', showline=True, linecolor='gray',
                       linewidth=1.5, mirror=True),
            font=dict(color='black', family='Arial')
        )

    return fig, f"<b>{title_text}</b><br><span style='font-size:12px;color:#64748B'>Interactive Explorer Output</span>"


@app.callback(
    [Output('stat-total-movies', 'children'), Output('stat-total-profit', 'children'),
     Output('stat-avg-rating', 'children'), Output('stat-top-genre', 'children')] +
    [Output(f'chart-{i}', 'figure') for i in range(1, 14)],
    [Input('genre-filter', 'value'), Input('language-filter', 'value'), Input('year-filter', 'value')]
)
def update_standard_charts(selected_genres, selected_languages, selected_years):
    if not selected_genres: selected_genres = top_genres
    if not selected_languages: selected_languages = available_languages

    filtered = df[
        (df['main_genre'].isin(selected_genres)) &
        (df['language_group'].isin(selected_languages)) &
        (df['release_year'] >= selected_years[0]) &
        (df['release_year'] <= selected_years[1])
        ].copy()

    if filtered.empty:
        empty_state = apply_standard_layout(get_empty_state("Adjust filters to explore data"), "No Data", "", "")
        return tuple(["0", "$0", "0.0", "-"] + [empty_state] * 13)

    # --- Compute Top Stats dynamically ---
    total_movies = f"{len(filtered):,}"

    total_profit_val = filtered['realistic_profit'].sum() if 'realistic_profit' in filtered.columns else filtered[
        'profit'].sum()
    if total_profit_val >= 1e9:
        total_profit_str = f"${total_profit_val / 1e9:.2f}B"
    else:
        total_profit_str = f"${total_profit_val / 1e6:.1f}M"

    avg_rating_str = f"{filtered['weighted_rating'].mean():.1f}"
    top_genre_str = filtered['main_genre'].value_counts().idxmax() if not filtered['main_genre'].empty else "-"

    # C1
    df_month = filtered.dropna(subset=['release_month']).groupby('release_month')['profit'].mean().reset_index()
    df_month['Month'] = df_month['release_month'].apply(lambda x: calendar.month_abbr[int(x)])
    colors1 = ['#93C5FD'] * len(df_month)
    if len(colors1) > 0: colors1[df_month['profit'].idxmax()] = COLOR_SUCCESS

    c1 = go.Figure(
        go.Bar(x=df_month['Month'], y=df_month['profit'], name="Profit Data",
               text=(df_month['profit'] / 1e6).round(1).astype(str) + 'M',
               textposition='outside', marker_color=colors1, marker_line_width=0, showlegend=False))
    c1.add_trace(go.Bar(x=[None], y=[None], marker_color=COLOR_SUCCESS, name='Top Performing Month'))
    c1.add_trace(go.Bar(x=[None], y=[None], marker_color='#93C5FD', name='Standard Month'))
    c1 = apply_standard_layout(
        c1,
        title_text="Average Profit by Release Season",
        xaxis_title="Release Month",
        yaxis_title="Avg Profit ($)",
        legend_title="Metrics",
        yaxis_rangemode="tozero"
    )

    # C2
    df_company = filtered.groupby('primary_company')['profit'].sum().reset_index()
    df_top15 = df_company[df_company['primary_company'] != 'Unknown'].sort_values('profit', ascending=False).head(
        15).sort_values('profit', ascending=True).reset_index(drop=True)
    colors2 = ['#93C5FD'] * len(df_top15)
    if len(colors2) > 0: colors2[-1] = COLOR_SUCCESS

    c2 = go.Figure(
        go.Bar(x=df_top15['profit'], y=df_top15['primary_company'], name="Total Profit Data", orientation='h',
               text=(df_top15['profit'] / 1e9).round(2).astype(str) + 'B', textposition='outside',
               marker_color=colors2, marker_line_width=0, showlegend=False))
    c2.add_trace(go.Bar(x=[None], y=[None], marker_color=COLOR_SUCCESS, name='Top Studio'))
    c2.add_trace(go.Bar(x=[None], y=[None], marker_color='#93C5FD', name='Other Studios'))
    c2 = apply_standard_layout(
        c2,
        title_text="Top 15 Production Companies by Total Profit",
        xaxis_title="Total Profit (USD)",
        yaxis_title="Production Company",
        legend_title="Metrics",
        xaxis_range=[0, df_top15['profit'].max() * 1.15 if not df_top15.empty else 1],
        margin_l=180
    )

    # C3
    tier_grp = filtered.dropna(subset=['Budget_Tier']).groupby(['Budget_Tier', 'performance_status'],
                                                               observed=True).size().unstack(fill_value=0)
    if not tier_grp.empty and 'Profit' in tier_grp.columns and 'Loss' in tier_grp.columns:
        tier_grp['Total'] = tier_grp.sum(axis=1)
        tier_grp['Profit_Pct'] = (tier_grp['Profit'] / tier_grp['Total'] * 100).fillna(0)
        tier_grp['Loss_Pct'] = (tier_grp['Loss'] / tier_grp['Total'] * 100).fillna(0)
        tier_grp = tier_grp.sort_values(by='Loss_Pct', ascending=False)
        p_colors = [COLOR_SUCCESS] * len(tier_grp.index)
        l_colors = [COLOR_DANGER] * len(tier_grp.index)

        c3 = go.Figure()
        c3.add_trace(go.Bar(x=tier_grp.index, y=tier_grp['Profit_Pct'], name='Profit Pct', marker_color=p_colors,
                            text=tier_grp['Profit_Pct'].round(0).astype(int).astype(str) + "%", textposition='inside',
                            insidetextanchor='middle', textfont=dict(color='white'), marker_line_width=0))
        c3.add_trace(go.Bar(x=tier_grp.index, y=tier_grp['Loss_Pct'], name='Loss Pct', marker_color=l_colors,
                            text=tier_grp['Loss_Pct'].round(0).astype(int).astype(str) + "%", textposition='inside',
                            insidetextanchor='middle', textfont=dict(color='white'), marker_line_width=0))
        c3 = apply_standard_layout(
            c3,
            title_text="Profit vs Loss Distribution by Budget Tier (%)",
            xaxis_title="Budget Tiers (Sorted by Risk Level)",
            yaxis_title="Percentage of Movies (%)",
            legend_title="Performance",
            barmode='stack',
            bargap=0.35,
            yaxis_range=[0, 125],
            yaxis_ticksuffix="%"
        )
    else:
        c3 = apply_standard_layout(get_empty_state("Not enough data"), "Data Unavailable", "", "")

    # C4
    c4_data = []
    genre_cols = [c for c in filtered.columns if c.startswith('genre_') and c != 'genre_list']
    for col in genre_cols:
        g_name = col.replace('genre_', '')[:10]
        high = filtered[(filtered[col] == 1) & (filtered['Rating_Cat'] == 'High Rated')].shape[0]
        low = filtered[(filtered[col] == 1) & (filtered['Rating_Cat'] == 'Low Rated')].shape[0]
        total = high + low
        if total > 0:
            c4_data.append({'Genre': g_name, 'High Rated': high, 'Low Rated': low, 'Total': total})

    df_g4 = pd.DataFrame(c4_data).sort_values('Total', ascending=True).tail(10).reset_index(
        drop=True) if c4_data else pd.DataFrame()

    c4 = go.Figure()
    if not df_g4.empty:
        df_g4['High_Pct'] = (df_g4['High Rated'] / df_g4['Total'] * 100).fillna(0).round(0).astype(int)
        df_g4['Low_Pct'] = (df_g4['Low Rated'] / df_g4['Total'] * 100).fillna(0).round(0).astype(int)

        h_col = ['#3B82F6' if g == 'Drama' else '#93C5FD' for g in df_g4['Genre']]
        l_col = ['#1E40AF' if g == 'Drama' else '#64748B' for g in df_g4['Genre']]

        for i, row in df_g4.iterrows():
            is_drama = row['Genre'] == 'Drama'
            c4.add_trace(go.Bar(
                y=[row['Genre']], x=[row['High Rated']], orientation='h',
                name='High Satisfaction (Drama Top)' if is_drama else 'High Satisfaction',
                marker_color=h_col[i], marker_line_width=0,
                text=str(row['High Rated']) if row['High Rated'] > 0 else '', textposition='inside',
                insidetextanchor='middle', textfont=dict(color='white', size=11, family='Inter'),
                showlegend=is_drama or i == 0
            ))
            c4.add_trace(go.Bar(
                y=[row['Genre']], x=[row['Low Rated']], orientation='h',
                name='Low Satisfaction (Drama Top)' if is_drama else 'Low Satisfaction',
                marker_color=l_col[i], marker_line_width=0,
                text=str(row['Low Rated']) if row['Low Rated'] > 0 else '', textposition='inside',
                insidetextanchor='middle', textfont=dict(color='white', size=11, family='Inter'),
                showlegend=is_drama or i == 0
            ))
            c4.add_annotation(
                x=row['Total'] + (df_g4['Total'].max() * 0.02),
                y=row['Genre'],
                text=f"Total: {row['Total']}",
                showarrow=False,
                font=dict(size=10, color='#475569', family='Inter', weight='bold'),
                xanchor='left', yanchor='middle', xref='x', yref='y'
            )

        c4 = apply_standard_layout(
            c4,
            title_text="Audience Satisfaction Composition by Genre",
            xaxis_title="Number of Movies",
            yaxis_title="Movie Genre",
            legend_title="Satisfaction Level",
            barmode='stack',
            bargap=0.25,
            bargroupgap=0.1,
            margin_l=120
        )
        max_total = df_g4['Total'].max() if not df_g4.empty else 1
        c4.update_xaxes(range=[0, max_total * 1.15])

    # C5
    df_month2 = filtered.dropna(subset=['release_month']).groupby('release_month')[
        ['weighted_rating', 'popularity']].mean().reset_index().sort_values('release_month')
    df_month2['Month'] = df_month2['release_month'].apply(lambda x: calendar.month_abbr[int(x)])
    df_month2['Norm_Rating'] = df_month2['weighted_rating'] * 10
    df_month2['Norm_Popularity'] = (df_month2['popularity'] / (df_month2['popularity'].max() or 1)) * 100

    c5 = go.Figure()
    c5.add_trace(
        go.Bar(x=df_month2['Month'], y=df_month2['Norm_Rating'], name='Audience Rating', marker_color='#60A5FA',
               marker_line_width=0, text="<b>" + df_month2['Norm_Rating'].round(0).astype(int).astype(str) + "</b>",
               textposition='outside', textfont=dict(color='black', family='Inter')))
    c5.add_trace(
        go.Bar(x=df_month2['Month'], y=df_month2['Norm_Popularity'], name='Marketing Hype', marker_color='#1E40AF',
               marker_line_width=0, text="<b>" + df_month2['Norm_Popularity'].round(0).astype(int).astype(str) + "</b>",
               textposition='outside', textfont=dict(color='black', family='Inter')))

    max_val_c5 = max(df_month2['Norm_Rating'].max() if not df_month2.empty else 0,
                     df_month2['Norm_Popularity'].max() if not df_month2.empty else 0)
    c5 = apply_standard_layout(
        c5,
        title_text="Audience Rating vs Marketing Hype by Release Month",
        xaxis_title="Release Month",
        yaxis_title="Score (0-100 Scale)",
        legend_title="Metrics",
        barmode='group',
        bargroupgap=0.15,
        yaxis_range=[0, max_val_c5 * 1.25],
        yaxis_rangemode="tozero"
    )

    # C6
    df_dec = filtered[filtered['Decade'] >= 1980].groupby('Decade_Str')[
        ['budget', 'profit']].mean().reset_index().sort_values('Decade_Str')
    c6 = go.Figure()
    c6.add_trace(go.Bar(y=df_dec['Decade_Str'], x=df_dec['budget'] / 1e6, name='Avg Budget', orientation='h',
                        marker_color='#94A3B8', marker_line_width=0,
                        text="<b>" + (df_dec['budget'] / 1e6).round(1).astype(str) + "M</b>", textposition='outside',
                        textfont=dict(color='black', family='Inter')))
    c6.add_trace(go.Bar(y=df_dec['Decade_Str'], x=df_dec['profit'] / 1e6, name='Avg Profit', orientation='h',
                        marker_color=COLOR_PRIMARY, marker_line_width=0,
                        text="<b>" + (df_dec['profit'] / 1e6).round(1).astype(str) + "M</b>", textposition='outside',
                        textfont=dict(color='black', family='Inter')))
    c6 = apply_standard_layout(
        c6,
        title_text="Average Budget vs Profit by Decade",
        xaxis_title="Amount ($ Millions)",
        yaxis_title="Decade",
        legend_title="Financials",
        barmode='group',
        bargap=0.2,
        bargroupgap=0.1,
        margin_l=80,
        xaxis_range=[0, max(df_dec['budget'].max(), df_dec['profit'].max()) / 1e6 * 1.25 if not df_dec.empty else 1]
    )

    # C7
    df_scatter = filtered.dropna(subset=['runtime', 'weighted_rating'])
    c7 = go.Figure()
    if not df_scatter.empty:
        c7.add_trace(
            go.Scatter(x=df_scatter['runtime'], y=df_scatter['weighted_rating'], mode='markers', name='Movies Scatter',
                       marker=dict(color=COLOR_PRIMARY, size=5, opacity=0.4, line_width=0),
                       text=df_scatter['title']))
        if len(df_scatter) > 1:
            m, b = np.polyfit(df_scatter['runtime'], df_scatter['weighted_rating'], 1)
            c7.add_trace(
                go.Scatter(x=df_scatter['runtime'], y=m * df_scatter['runtime'] + b, mode='lines',
                           name='Linear Trendline',
                           line=dict(color='#1E40AF', width=2, dash='dot')))
    c7 = apply_standard_layout(
        c7,
        title_text="Runtime vs. Audience Rating",
        xaxis_title="Runtime (Minutes)",
        yaxis_title="Weighted Rating",
        legend_title="Distribution"
    )

    # C8
    df_bub = filtered[(filtered['profit'] > 0) & (filtered['budget'] > 0) & (filtered['vote_count'] > 100)].copy()
    c8 = go.Figure()
    if not df_bub.empty:
        sizeref = 2.0 * df_bub['budget'].max() / (35 ** 2)
        c8.add_trace(go.Scatter(x=df_bub['vote_count'], y=df_bub['profit'], mode='markers', text=df_bub['title'],
                                name='Profit relative to Votes',
                                marker=dict(size=df_bub['budget'], sizeref=sizeref, sizemode='area',
                                            color=COLOR_PRIMARY, opacity=0.4, line=dict(color='#FFFFFF', width=0.5)),
                                showlegend=True))
    c8 = apply_standard_layout(
        c8,
        title_text="Audience Engagement vs. Profitability",
        xaxis_title="Vote Count",
        yaxis_title="Profit ($)",
        legend_title="Metrics"
    )

    # C9
    c9 = go.Figure(
        go.Histogram(x=filtered['runtime'], xbins=dict(start=40, end=250, size=9), name="Movies Frequency",
                     marker_color=COLOR_PRIMARY,
                     marker_line_width=0))
    if not filtered.empty and not filtered['runtime'].isna().all():
        c9.add_vline(x=filtered['runtime'].mean(), line_dash="dash", line_color=COLOR_SECONDARY,
                     name="Mean Runtime Line")
    c9 = apply_standard_layout(
        c9,
        title_text="Distribution of Movie Runtime (Industry Standard)",
        xaxis_title="Runtime (Minutes)",
        yaxis_title="Number of Movies",
        legend_title="Legend"
    )

    # C10
    season_order = ['Winter', 'Spring', 'Summer', 'Autumn']
    c10 = go.Figure()
    for season in season_order:
        c10.add_trace(
            go.Box(x=filtered[filtered['Season'] == season]['Season'], y=filtered[filtered['Season'] == season]['ROI'],
                   name=season, marker_color=COLOR_PRIMARY, fillcolor='#F8FAFC', line_width=1))
    c10 = apply_standard_layout(
        c10,
        title_text="ROI Distribution by Season (Volatility Comparison)",
        xaxis_title="Season",
        yaxis_title="ROI Multiplier",
        legend_title="Seasons",
        xaxis_categoryorder='array',
        xaxis_categoryarray=season_order,
        yaxis_range=[0, 10]
    )

    # C11
    c11 = go.Figure()
    if not filtered.empty and 'performance_status' in filtered.columns:
        median_profit = filtered[filtered['performance_status'] == 'Profit']['log_budget'].median()
        median_loss = filtered[filtered['performance_status'] == 'Loss']['log_budget'].median()

        c11.add_trace(go.Violin(
            x=filtered['performance_status'][filtered['performance_status'] == 'Profit'],
            y=filtered['log_budget'][filtered['performance_status'] == 'Profit'],
            name='Profit',
            fillcolor='#A9D18E',
            line_color='black',
            box_visible=True,
            opacity=0.9
        ))
        c11.add_trace(go.Violin(
            x=filtered['performance_status'][filtered['performance_status'] == 'Loss'],
            y=filtered['log_budget'][filtered['performance_status'] == 'Loss'],
            name='Loss',
            fillcolor='#FF6666',
            line_color='black',
            box_visible=True,
            opacity=0.9
        ))

    c11 = apply_standard_layout(
        c11,
        title_text="Where Does Failure Lie? Budget Distribution by Performance",
        xaxis_title="Performance Status",
        yaxis_title="Log Budget",
        legend_title="Status Category"
    )

    # Adding the median annotations inside the callback to remain dynamic
    if not filtered.empty and 'performance_status' in filtered.columns:
        if pd.notna(median_profit):
            c11.add_annotation(
                x='Profit',
                y=median_profit,
                text=f"<b>{median_profit:.2f}</b>",
                showarrow=False,
                xshift=45,
                font=dict(color='black', size=12, family="Arial")
            )
        if pd.notna(median_loss):
            c11.add_annotation(
                x='Loss',
                y=median_loss,
                text=f"<b>{median_loss:.2f}</b>",
                showarrow=False,
                xshift=45,
                font=dict(color='black', size=12, family="Arial")
            )

    # Apply specific styling to match the Violin plot guideline
    c11.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(color='black', showgrid=False, showline=True, linecolor='gray', linewidth=1.5, mirror=True),
        yaxis=dict(color='black', showgrid=True, gridcolor='gray', griddash='dash', showline=True, linecolor='gray',
                   linewidth=1.5, mirror=True),
        font=dict(color='black', family='Arial')
    )

    # C12 (Fixed drop off in 2017)
    df_ts = filtered[
        (filtered['release_year'] >= 1990) & (filtered['release_year'] < 2017) & (filtered['revenue'] > 0)].groupby(
        'release_year')[
        ['budget', 'revenue']].mean().reset_index().sort_values('release_year')
    c12 = go.Figure()
    c12.add_trace(go.Scatter(x=df_ts['release_year'], y=df_ts['budget'], mode='lines+markers', name='Avg Budget',
                             line=dict(color=COLOR_DANGER, width=2)))
    c12.add_trace(go.Scatter(x=df_ts['release_year'], y=df_ts['revenue'], mode='lines+markers', name='Avg Revenue',
                             line=dict(color=COLOR_SUCCESS, width=2)))
    c12 = apply_standard_layout(
        c12,
        title_text="Budget vs Revenue Growth (Post-1990)",
        xaxis_title="Release Year",
        yaxis_title="Amount ($)",
        legend_title="Metrics"
    )

    # C13
    df_clean_area = filtered[(filtered['release_year'] >= 1990) & (filtered['release_year'] < 2017)]
    c13 = go.Figure()
    top_4 = ['Action', 'Comedy', 'Drama', 'Adventure']
    colors_area = ['rgba(37, 99, 235, 0.8)', 'rgba(96, 165, 250, 0.8)', 'rgba(147, 197, 253, 0.8)',
                   'rgba(191, 219, 254, 0.8)']
    for i, g in enumerate(top_4):
        if f'genre_{g}' in df_clean_area.columns:
            temp = df_clean_area[df_clean_area[f'genre_{g}'] == 1].groupby('release_year')['profit'].sum().reset_index()
            c13.add_trace(
                go.Scatter(x=temp['release_year'], y=temp['profit'], mode='lines', name=f"{g} Profit", stackgroup='one',
                           fillcolor=colors_area[i], line_width=0))
    c13 = apply_standard_layout(
        c13,
        title_text="Genre Contribution to Total Profit Over Time",
        xaxis_title="Release Year",
        yaxis_title="Cumulative Profit ($)",
        legend_title="Genres"
    )

    figures = [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13]
    return tuple([total_movies, total_profit_str, avg_rating_str, top_genre_str] + figures)


# --- EXPLORER CALLBACKS ---
@app.callback(
    [Output('custom-x-axis-container', 'style'), Output('custom-x-axis', 'options'), Output('custom-x-axis', 'value'),
     Output('x-axis-label', 'children'),
     Output('custom-y-axis-container', 'style'), Output('custom-y-axis', 'options'), Output('custom-y-axis', 'value'),
     Output('y-axis-label', 'children'),
     Output('custom-group-axis-container', 'style'), Output('custom-group-axis', 'options'),
     Output('custom-group-axis', 'value'), Output('group-axis-label', 'children'),
     Output('custom-size-axis-container', 'style'), Output('custom-size-axis', 'options'),
     Output('custom-size-axis', 'value'), Output('size-axis-label', 'children')],
    [Input('custom-chart-type', 'value')]
)
def update_custom_dropdowns(chart_type):
    show_style = {'display': 'block'}
    hide_style = {'display': 'none'}

    num_opts = [{'label': col.replace('_', ' ').title(), 'value': col} for col in NUMERICAL_COLS]
    cat_opts = [{'label': col.replace('_', ' ').title(), 'value': col} for col in CATEGORICAL_COLS]
    all_opts = num_opts + cat_opts

    all_none = [{'label': 'None', 'value': 'None'}] + all_opts
    cat_none = [{'label': 'None', 'value': 'None'}] + cat_opts
    num_none = [{'label': 'None', 'value': 'None'}] + num_opts

    x_style, x_opts, x_val, x_label = show_style, all_opts, 'budget', "X-Axis:"
    y_style, y_opts, y_val, y_label = show_style, all_none, 'revenue', "Y-Axis:"
    g_style, g_opts, g_val, g_label = show_style, cat_none, 'None', "Color / Group:"
    s_style, s_opts, s_val, s_label = show_style, num_none, 'None', "Size (Bubble):"

    if chart_type == 'scatter':
        x_val, y_val, s_style = 'budget', 'revenue', hide_style
    elif chart_type == 'bubble':
        x_val, y_val, s_val = 'budget', 'revenue', 'popularity'
    elif chart_type == 'histogram':
        x_val, y_style, y_val, s_style = 'vote_average', hide_style, 'None', hide_style
    elif chart_type in ['column', 'stacked_column', 'clustered_column']:
        x_val, y_val, s_style = 'main_genre', 'profit', hide_style
    elif chart_type in ['bar', 'stacked_bar', 'clustered_bar']:
        x_val, y_val, s_style = 'profit', 'primary_company', hide_style
    elif chart_type in ['box', 'violin']:
        x_val, y_val, s_style = 'Season', 'ROI', hide_style
    elif chart_type in ['line', 'area']:
        x_val, y_val, s_style = 'release_year', 'revenue', hide_style
    else:
        x_val, y_val, s_style = 'budget', 'revenue', hide_style

    return (x_style, x_opts, x_val, x_label,
            y_style, y_opts, y_val, y_label,
            g_style, g_opts, g_val, g_label,
            s_style, s_opts, s_val, s_label)


@app.callback(
    [Output('custom-graph-output', 'figure'),
     Output('custom-chart-title', 'children')],
    [Input('genre-filter', 'value'), Input('language-filter', 'value'), Input('year-filter', 'value'),
     Input('custom-chart-type', 'value'), Input('custom-x-axis', 'value'), Input('custom-y-axis', 'value'),
     Input('custom-group-axis', 'value'), Input('custom-size-axis', 'value'), Input('custom-top-n', 'value')]
)
def update_custom_graph(selected_genres, selected_languages, selected_years, chart_type, x_col, y_col, group_col,
                        size_col, top_n):
    if not selected_genres: selected_genres = top_genres
    if not selected_languages: selected_languages = available_languages

    filtered = df[
        (df['main_genre'].isin(selected_genres)) &
        (df['language_group'].isin(selected_languages)) &
        (df['release_year'] >= selected_years[0]) &
        (df['release_year'] <= selected_years[1])
        ]

    fig, title_html = build_dynamic_chart(filtered, chart_type, x_col, y_col, group_col, size_col, top_n)

    # Clean the title format safely
    clean_title = title_html.replace("<b>", "").replace("</b>", "").split("<br>")[0]

    return fig, clean_title


if __name__ == '__main__':
    app.run_server(debug=True)