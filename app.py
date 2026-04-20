import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# ==========================================
# 1. DATA LOADING & PREPARATION
# ==========================================

# Load the cleaned dataset
df = pd.read_csv('data/cleaned_movies.csv')

# Get the top 5 most frequent genres to make the dropdown and visuals cleaner
top_genres = df['main_genre'].value_counts().nlargest(5).index.tolist()

# Get available languages from the new language_group column
available_languages = df['language_group'].unique().tolist()

# Filter the dataframe to only include these top 5 genres initially
df = df[df['main_genre'].isin(top_genres)]

# Initialize the Dash web application
# Added assets_ignore='.*~' to prevent FileNotFoundError from temporary editor files
app = dash.Dash(__name__, assets_ignore='.*~')

# ==========================================
# 2. APP LAYOUT (FRONTEND)
# ==========================================

app.layout = html.Div(className='container', children=[

    # Dashboard Header
    html.H1("Movie Industry Analysis Dashboard", className='header-title'),

    # --- Interactive Filters Section ---
    html.Div(className='filters-section', children=[

        # Filter 1: Genre Dropdown
        html.Div(className='filter-control', children=[
            html.Label("Select Genre:"),
            dcc.Dropdown(
                id='genre-filter',
                options=[{'label': g, 'value': g} for g in top_genres],
                value=top_genres[0],  # Default value is the first top genre
                clearable=False
            )
        ]),

        # Filter 2: Release Year Range Slider
        html.Div(className='filter-control', style={'width': '40%'}, children=[
            html.Label("Release Year Range:"),
            dcc.RangeSlider(
                id='year-filter',
                min=df['release_year'].min(),
                max=df['release_year'].max(),
                step=1,
                value=[2000, 2016],  # Default selected range
                marks={year: str(year) for year in range(1980, 2020, 10)}
            )
        ]),

        # Filter 3: Language Group Dropdown (Updated for Professional Cleaning)
        html.Div(className='filter-control', style={'width': '20%'}, children=[
            html.Label("Language Group:"),
            dcc.Dropdown(
                id='lang-filter',
                options=[{'label': l, 'value': l} for l in available_languages],
                value='en',  # Default is English
                clearable=False
            )
        ])
    ]),

    # --- Charts Grid Section ---
    html.Div(className='charts-grid', children=[

        # Week 1 Charts (Comparison)
        html.Div(className='chart-card', children=[
            html.Span("Horizontal Bar Chart", className='chart-badge'),
            dcc.Graph(id='bar-chart'),
            html.P("Insight: Highlights the top 10 movies by revenue within the selected category.",
                   className='insight-text')
        ]),
        html.Div(className='chart-card', children=[
            html.Span("Column Chart", className='chart-badge'),
            dcc.Graph(id='col-chart'),
            html.P("Insight: Compares the production budgets of the top 10 movies.", className='insight-text')
        ]),

        # Week 2 Charts (Advanced Comparison)
        html.Div(className='chart-card', children=[
            html.Span("Stacked Column Chart", className='chart-badge'),
            dcc.Graph(id='stacked-col'),
            html.P("Insight: Breaks down annual revenue by genre to show trends over time.", className='insight-text')
        ]),
        html.Div(className='chart-card', children=[
            html.Span("Stacked Bar Chart", className='chart-badge'),
            dcc.Graph(id='stacked-bar'),
            html.P("Insight: Combined view of average budget and revenue per genre.", className='insight-text')
        ]),
        html.Div(className='chart-card', children=[
            html.Span("Clustered Column Chart", className='chart-badge'),
            dcc.Graph(id='cluster-col'),
            html.P("Insight: Directly compares total budget spending across genres each year.",
                   className='insight-text')
        ]),
        html.Div(className='chart-card', children=[
            html.Span("Clustered Bar Chart", className='chart-badge'),
            dcc.Graph(id='cluster-bar'),
            html.P("Insight: Side-by-side comparison of average budget vs. revenue by genre.", className='insight-text')
        ]),

        # Week 3 & 4 Charts (Relationship - Using Log Scale)
        html.Div(className='chart-card', children=[
            html.Span("Scatter Chart (Log Scale)", className='chart-badge'),
            dcc.Graph(id='scatter-chart'),
            html.P(
                "Insight: Visualizes the correlation between movie budgets and final revenues using Log transformation.",
                className='insight-text')
        ]),
        html.Div(className='chart-card', children=[
            html.Span("Bubble Chart", className='chart-badge'),
            dcc.Graph(id='bubble-chart'),
            html.P("Insight: Explores budget vs revenue, with bubble size reflecting audience popularity.",
                   className='insight-text')
        ]),

        # Week 5, 6 & 7 Charts (Distribution)
        html.Div(className='chart-card full-width', children=[
            html.Span("Histogram Chart (Log Scale)", className='chart-badge'),
            dcc.Graph(id='hist-chart'),
            html.P("Insight: Displays the frequency distribution of movie revenues on a Log scale.",
                   className='insight-text')
        ]),
        html.Div(className='chart-card', children=[
            html.Span("Box Chart", className='chart-badge'),
            dcc.Graph(id='box-chart'),
            html.P("Insight: Summarizes the distribution of audience ratings across genres.", className='insight-text')
        ]),
        html.Div(className='chart-card', children=[
            html.Span("Violin Chart", className='chart-badge'),
            dcc.Graph(id='violin-chart'),
            html.P("Insight: Shows the density and range of movie runtimes across genres.", className='insight-text')
        ]),

        # Week 8 & 9 Charts (Time-Series)
        html.Div(className='chart-card', children=[
            html.Span("Line Chart", className='chart-badge'),
            dcc.Graph(id='line-chart'),
            html.P("Insight: Tracks the volume of movie releases per year.", className='insight-text')
        ]),
        html.Div(className='chart-card', children=[
            html.Span("Area Chart", className='chart-badge'),
            dcc.Graph(id='area-chart'),
            html.P("Insight: Illustrates the cumulative growth of total movie revenue over time.",
                   className='insight-text')
        ])
    ])
])


# ==========================================
# 3. CALLBACKS (BACKEND LOGIC)
# ==========================================

@app.callback(
    [Output('bar-chart', 'figure'), Output('col-chart', 'figure'),
     Output('stacked-col', 'figure'), Output('stacked-bar', 'figure'),
     Output('cluster-col', 'figure'), Output('cluster-bar', 'figure'),
     Output('scatter-chart', 'figure'), Output('bubble-chart', 'figure'),
     Output('hist-chart', 'figure'), Output('box-chart', 'figure'),
     Output('violin-chart', 'figure'), Output('line-chart', 'figure'), Output('area-chart', 'figure')],
    [Input('genre-filter', 'value'), Input('year-filter', 'value'), Input('lang-filter', 'value')]
)
def update_dashboard(genre, year_range, lang):
    # 3.1 Apply Filters based on user input
    filtered = df[(df['release_year'] >= year_range[0]) & (df['release_year'] <= year_range[1])]

    # Use the new language_group column for filtering
    filtered = filtered[filtered['language_group'] == lang]

    # 3.2 Prepare specific DataFrames for different charts
    genre_data = filtered[filtered['main_genre'] == genre]
    top10_movies = genre_data.nlargest(10, 'revenue')
    yearly_data = filtered.groupby(['release_year', 'main_genre'])[['budget', 'revenue']].sum().reset_index()
    yearly_agg = filtered.groupby('release_year')[['revenue']].agg(
        {'revenue': ['sum', 'count']}).reset_index()
    yearly_agg.columns = ['release_year', 'revenue_sum', 'movie_count']

    genre_agg = filtered.groupby('main_genre')[['budget', 'revenue']].mean().reset_index()

    # 3.3 Create the 13 Plotly Figures
    modern_theme = 'plotly_white'
    primary_color = '#4318FF'

    # Week 1: Comparison
    fig_col = px.bar(top10_movies, x='title', y='revenue', title=f"Top 10 {genre} Movies (Revenue)",
                     template=modern_theme, color_discrete_sequence=[primary_color])
    fig_bar = px.bar(top10_movies, x='budget', y='title', orientation='h', title=f"Top 10 {genre} Movies (Budget)",
                     template=modern_theme, color_discrete_sequence=[primary_color])

    # Week 2: Stacked & Clustered
    fig_stacked_col = px.bar(yearly_data, x='release_year', y='revenue', color='main_genre',
                             title="Revenue by Year & Genre", barmode='stack', template=modern_theme)
    fig_cluster_col = px.bar(yearly_data, x='release_year', y='budget', color='main_genre',
                             title="Budget by Year & Genre", barmode='group', template=modern_theme)

    fig_stacked_bar = go.Figure(data=[
        go.Bar(name='Budget', y=genre_agg['main_genre'], x=genre_agg['budget'], orientation='h'),
        go.Bar(name='Revenue', y=genre_agg['main_genre'], x=genre_agg['revenue'], orientation='h')
    ]).update_layout(barmode='stack', title="Avg Budget & Revenue by Genre (Stacked)", template=modern_theme)

    fig_cluster_bar = go.Figure(data=[
        go.Bar(name='Budget', y=genre_agg['main_genre'], x=genre_agg['budget'], orientation='h'),
        go.Bar(name='Revenue', y=genre_agg['main_genre'], x=genre_agg['revenue'], orientation='h')
    ]).update_layout(barmode='group', title="Avg Budget vs Revenue by Genre (Clustered)", template=modern_theme)

    # Week 3 & 4: Relationship (Updated with Log Columns from preprocessing)
    fig_scatter = px.scatter(genre_data, x='log_budget', y='log_revenue', title="Budget vs Revenue (Log Scale)",
                             template=modern_theme,
                             color_discrete_sequence=[primary_color], hover_name='title')
    fig_bubble = px.scatter(genre_data, x='budget', y='revenue', size='popularity', hover_name='title',
                            title="Industry Matrix (Size = Popularity)", template=modern_theme,
                            color_discrete_sequence=[primary_color])

    # Week 5, 6, 7: Distribution (Updated with Log Column)
    fig_hist = px.histogram(filtered, x='log_revenue', color='main_genre', title="Revenue Distribution (Log Scale)",
                            template=modern_theme)
    fig_box = px.box(filtered, x='main_genre', y='vote_average', color='main_genre', title="Ratings Distribution",
                     template=modern_theme)
    fig_violin = px.violin(filtered, x='main_genre', y='runtime', color='main_genre', box=True,
                           title="Runtime Distribution", template=modern_theme)

    # Week 8 & 9: Time-Series
    fig_line = px.line(yearly_agg, x='release_year', y='movie_count', markers=True, title="Movies Released per Year",
                       template=modern_theme, color_discrete_sequence=[primary_color])
    fig_area = px.area(yearly_agg, x='release_year', y='revenue_sum', title="Total Revenue Over Time",
                       template=modern_theme, color_discrete_sequence=[primary_color])

    return (fig_bar, fig_col, fig_stacked_col, fig_stacked_bar,
            fig_cluster_col, fig_cluster_bar, fig_scatter, fig_bubble,
            fig_hist, fig_box, fig_violin, fig_line, fig_area)


if __name__ == '__main__':
    app.run_server(debug=True)