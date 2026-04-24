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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DATA_PATH = os.path.join(BASE_DIR, 'data', 'raw_movies.csv')
CLEAN_DATA_PATH = os.path.join(BASE_DIR, 'data', 'cleaned_movies.csv')

if not os.path.exists(CLEAN_DATA_PATH):
    print(f"\n[INFO] Clean dataset missing. Auto-building pipeline from raw data...")
    if not os.path.exists(RAW_DATA_PATH):
        raise FileNotFoundError(f"Raw data missing at {RAW_DATA_PATH}")
    process_pipeline(RAW_DATA_PATH, CLEAN_DATA_PATH)
    print("[INFO] Pipeline complete. Starting dashboard...\n")

df = pd.read_csv(CLEAN_DATA_PATH)

validate_dataset(df)

top_genres = df['main_genre'].value_counts().nlargest(5).index.tolist()
available_languages = df['language_group'].dropna().unique().tolist()
min_year = int(df['release_year'].min())
max_year = int(df['release_year'].max())

NUMERICAL_COLS = [
    'budget', 'revenue', 'profit', 'ROI', 'log_budget', 'log_revenue',
    'runtime', 'vote_average', 'weighted_rating', 'popularity', 'popularity_score', 'vote_count'
]
CATEGORICAL_COLS = [
    'main_genre', 'performance_status', 'revenue_flag', 'language_group',
    'release_year', 'Season', 'Budget_Tier', 'Rating_Cat', 'Decade_Str', 'primary_company'
]

# SaaS Professional Color Palette
COLOR_PRIMARY = '#2563EB'
COLOR_SUCCESS = '#16A34A'
COLOR_DANGER = '#DC2626'
COLOR_SECONDARY = '#64748B'
COLOR_BORDER = '#CBD5E1'

# Array of blue variations for grouped charts
GUIDELINE_COLORS = ['#2563EB', '#3B82F6', '#60A5FA', '#93C5FD', '#1D4ED8', '#1E40AF', '#1E3A8A']

df = df[df['main_genre'].isin(top_genres)]

app = dash.Dash(__name__, assets_ignore='.*~')
app.title = "Movie Analytics"


def create_chart_card(chart_id, title, relation, insight, full_width=False):
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


app.layout = html.Div(className='app-container', children=[
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

    html.Div(className='main-content', children=[
        html.Div(className='top-header', children=[
            html.H1("Overview", className='page-title')
        ]),

        html.Div(className='top-stats-grid', children=[
            html.Div(className='stat-card', children=[
                html.P("Total Movies", className='stat-title'),
                html.H3(id='stat-total-movies', className='stat-value')
            ]),
            html.Div(className='stat-card', children=[
                html.P("Total Profit", className='stat-title'),
                html.H3(id='stat-total-profit', className='stat-value')
            ]),
            html.Div(className='stat-card', children=[
                html.P("Average Rating", className='stat-title'),
                html.H3(id='stat-avg-rating', className='stat-value')
            ]),
            html.Div(className='stat-card', children=[
                html.P("Top Genre", className='stat-title'),
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
                              "Vast majority of successful films congregate within the 80–120-minute window.", False),
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
            create_chart_card('chart-12', "12. Time-Series Analysis: Average Budget vs. Revenue Trends (1990–2017)",
                              "Year vs Amount", "Revenue remains highly volatile, confirming a hit-driven industry.",
                              True),
            create_chart_card('chart-13', "13. Area Chart: Genre Contribution to Total Profit Over Time",
                              "Year vs Cumulative Profit",
                              "Action and Adventure dominate total profit growth post-2010.", True),
        ]),

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
            ])
        ])
    ])
])


def apply_guidelines(fig):
    """Applies modern SaaS styling: soft borders, clean fonts, minimal grids."""
    fig.update_layout(
        plot_bgcolor='#FFFFFF',
        paper_bgcolor='#FFFFFF',
        font=dict(color='#334155', family='Inter', size=12),
        margin=dict(t=20, b=40, l=40, r=20)
    )
    fig.update_xaxes(
        color='#64748B', showline=True, linecolor=COLOR_BORDER,
        linewidth=1, mirror=False, gridcolor='#F1F5F9', zerolinecolor='#E2E8F0'
    )
    fig.update_yaxes(
        color='#64748B', showline=True, linecolor=COLOR_BORDER,
        linewidth=1, mirror=False, gridcolor='#F1F5F9', zerolinecolor='#E2E8F0'
    )
    return fig


def get_empty_state(message):
    """Returns a clean empty state graphic."""
    fig = go.Figure()
    fig.add_annotation(text=message, x=0.5, y=0.5, showarrow=False, font=dict(color="#64748B", size=14))
    fig.update_layout(plot_bgcolor='#FFFFFF', paper_bgcolor='#FFFFFF', xaxis=dict(visible=False),
                      yaxis=dict(visible=False))
    return fig


# --- SMART DYNAMIC CHART BUILDER ---
def build_dynamic_chart(df_filtered, chart_type, x_col, y_col, group_col, size_col):
    if not x_col or x_col == 'None':
        return apply_guidelines(get_empty_state("Select an X-Axis to begin exploration")), "Interactive Explorer Output"

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
        fig.add_annotation(text=error_msg, x=0.5, y=0.5, showarrow=False, font=dict(color=COLOR_DANGER, size=14))
        fig.update_layout(plot_bgcolor='#FEF2F2', paper_bgcolor='#FFFFFF', xaxis=dict(visible=False),
                          yaxis=dict(visible=False))
        return fig, "Configuration Error"

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
                                     marker_line_width=0))
            else:
                calc_x = x_col if x_is_cat else y_col
                calc_y = y_col if x_is_cat else x_col
                agg = df_g.groupby(calc_x)[calc_y].mean().reset_index()
                fig.add_trace(
                    go.Bar(x=agg[calc_x], y=agg[calc_y], name=trace_name, marker_color=c_val, marker_line_width=0))

        elif chart_type in ['bar', 'stacked_bar', 'clustered_bar']:
            if is_count_based:
                val_counts = df_g[x_col].value_counts().reset_index()
                val_counts.columns = [x_col, 'Count']
                fig.add_trace(go.Bar(y=val_counts[x_col], x=val_counts['Count'], orientation='h', name=trace_name,
                                     marker_color=c_val, marker_line_width=0))
            else:
                calc_x = x_col if x_is_num else y_col
                calc_y = y_col if x_is_num else x_col
                agg = df_g.groupby(calc_y)[calc_x].mean().reset_index()
                fig.add_trace(go.Bar(y=agg[calc_y], x=agg[calc_x], orientation='h', name=trace_name, marker_color=c_val,
                                     marker_line_width=0))

        elif chart_type == 'box':
            if x_is_cat:
                fig.add_trace(
                    go.Box(x=df_g[x_col], y=df_g[y_col] if y_col else df_g[NUMERICAL_COLS[0]], name=trace_name,
                           marker_color=c_val, line_width=1))
            else:
                fig.add_trace(go.Box(x=df_g[x_col], y=df_g[y_col] if y_col else None, orientation='h', name=trace_name,
                                     marker_color=c_val, line_width=1))

        elif chart_type == 'violin':
            if x_is_cat:
                fig.add_trace(
                    go.Violin(x=df_g[x_col], y=df_g[y_col] if y_col else df_g[NUMERICAL_COLS[0]], name=trace_name,
                              line_color=c_val, fillcolor=c_val, meanline_visible=True))
            else:
                fig.add_trace(
                    go.Violin(x=df_g[x_col], y=df_g[y_col] if y_col else None, orientation='h', name=trace_name,
                              line_color=c_val, fillcolor=c_val, meanline_visible=True))

        elif chart_type == 'line':
            agg = df_g.groupby(x_col)[y_col].mean().reset_index()
            fig.add_trace(go.Scatter(x=agg[x_col], y=agg[y_col], mode='lines+markers', name=trace_name,
                                     line=dict(color=c_val, width=2)))

        elif chart_type == 'area':
            agg = df_g.groupby(x_col)[y_col].sum().reset_index()
            fig.add_trace(
                go.Scatter(x=agg[x_col], y=agg[y_col], mode='lines', stackgroup='one', name=trace_name, fillcolor=c_val,
                           line_width=0))

    if chart_type in ['stacked_column', 'stacked_bar']:
        fig.update_layout(barmode='stack')
    elif chart_type in ['clustered_column', 'clustered_bar']:
        fig.update_layout(barmode='group')
    elif chart_type == 'histogram':
        fig.update_layout(barmode='overlay')

    y_label = y_col.replace('_', ' ').title() if y_col else ("Count" if is_count_based else "")
    x_label = x_col.replace('_', ' ').title()

    if chart_type in ['bar', 'stacked_bar', 'clustered_bar'] and not is_count_based:
        if x_is_num:
            y_label, x_label = x_label, y_col.replace('_', ' ').title()

    title_text = f"{y_label} vs {x_label}" if y_label else f"Distribution of {x_label}"

    fig.update_layout(
        xaxis=dict(title=x_label),
        yaxis=dict(title=y_label),
        showlegend=True if group_col else False
    )
    return apply_guidelines(
        fig), f"<b>{title_text}</b><br><span style='font-size:12px;color:#64748B'>Interactive Explorer Output</span>"


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
        empty_state = get_empty_state("Adjust filters to explore data")
        return tuple(["0", "$0", "0.0", "-"] + [empty_state] * 13)

    # --- Compute Top Stats dynamically ---
    total_movies = f"{len(filtered):,}"

    total_profit_val = filtered['profit'].sum()
    if total_profit_val >= 1e9:
        total_profit_str = f"${total_profit_val / 1e9:.2f}B"
    else:
        total_profit_str = f"${total_profit_val / 1e6:.1f}M"

    avg_rating_str = f"{filtered['vote_average'].mean():.1f}"
    top_genre_str = filtered['main_genre'].value_counts().idxmax() if not filtered['main_genre'].empty else "-"

    # C1
    df_month = filtered.dropna(subset=['release_month']).groupby('release_month')['profit'].mean().reset_index()
    df_month['Month'] = df_month['release_month'].apply(lambda x: calendar.month_abbr[int(x)])
    colors1 = ['#93C5FD'] * len(df_month)
    if len(colors1) > 0: colors1[df_month['profit'].idxmax()] = COLOR_SUCCESS
    c1 = go.Figure(
        go.Bar(x=df_month['Month'], y=df_month['profit'], text=(df_month['profit'] / 1e6).round(1).astype(str) + 'M',
               textposition='outside', marker_color=colors1, marker_line_width=0))
    c1.update_layout(xaxis=dict(showgrid=False), yaxis=dict(showgrid=True))

    # C2
    df_company = filtered.groupby('primary_company')['profit'].sum().reset_index()
    df_top15 = df_company[df_company['primary_company'] != 'Unknown'].sort_values('profit', ascending=False).head(
        15).sort_values('profit', ascending=True).reset_index(drop=True)
    colors2 = ['#93C5FD'] * len(df_top15)
    if len(colors2) > 0: colors2[-1] = COLOR_SUCCESS
    c2 = go.Figure(go.Bar(x=df_top15['profit'], y=df_top15['primary_company'], orientation='h',
                          text=(df_top15['profit'] / 1e9).round(2).astype(str) + 'B', textposition='outside',
                          marker_color=colors2, marker_line_width=0))
    c2.update_layout(xaxis=dict(showgrid=True, range=[0, df_top15['profit'].max() * 1.15 if not df_top15.empty else 1]),
                     yaxis=dict(showgrid=False))

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
        c3.update_layout(barmode='stack', bargap=0.35, yaxis=dict(range=[0, 125], ticksuffix="%"),
                         legend=dict(yanchor="bottom", y=-0.25, xanchor="center", x=0.5, orientation="h"))
    else:
        c3 = get_empty_state("Not enough data")

    # C4
    c4_data = []
    genre_cols = [c for c in filtered.columns if c.startswith('genre_') and c != 'genre_list']
    for col in genre_cols:
        g_name = col.replace('genre_', '')[:10]
        high = filtered[(filtered[col] == 1) & (filtered['Rating_Cat'] == 'High Rated')].shape[0]
        low = filtered[(filtered[col] == 1) & (filtered['Rating_Cat'] == 'Low Rated')].shape[0]
        total = high + low
        if total > 0: c4_data.append({'Genre': g_name, 'High Rated': high, 'Low Rated': low, 'Total': total})
    df_g4 = pd.DataFrame(c4_data).sort_values('Total', ascending=True).tail(10).reset_index(
        drop=True) if c4_data else pd.DataFrame()
    c4 = go.Figure()
    if not df_g4.empty:
        c4.add_trace(go.Bar(y=df_g4['Genre'], x=df_g4['High Rated'], name='High Satisfaction', orientation='h',
                            marker_color=COLOR_PRIMARY, marker_line_width=0))
        c4.add_trace(go.Bar(y=df_g4['Genre'], x=df_g4['Low Rated'], name='Low Satisfaction', orientation='h',
                            marker_color=COLOR_SECONDARY, marker_line_width=0))
        c4.update_layout(barmode='stack', bargap=0.3, xaxis=dict(showgrid=True), yaxis=dict(showgrid=False),
                         legend=dict(yanchor="bottom", y=-0.25, xanchor="center", x=0.5, orientation="h"))

    # C5
    df_month2 = filtered.dropna(subset=['release_month']).groupby('release_month')[
        ['weighted_rating', 'popularity']].mean().reset_index().sort_values('release_month')
    df_month2['Month'] = df_month2['release_month'].apply(lambda x: calendar.month_abbr[int(x)])
    df_month2['Norm_Rating'] = df_month2['weighted_rating'] * 10
    df_month2['Norm_Popularity'] = (df_month2['popularity'] / (df_month2['popularity'].max() or 1)) * 100
    c5 = go.Figure()
    c5.add_trace(go.Bar(x=df_month2['Month'], y=df_month2['Norm_Rating'], name='Rating', marker_color='#60A5FA',
                        marker_line_width=0))
    c5.add_trace(go.Bar(x=df_month2['Month'], y=df_month2['Norm_Popularity'], name='Popularity', marker_color='#1E40AF',
                        marker_line_width=0))
    max_val_c5 = max(df_month2['Norm_Rating'].max() if not df_month2.empty else 0,
                     df_month2['Norm_Popularity'].max() if not df_month2.empty else 0)
    c5.update_layout(barmode='group', bargroupgap=0.15,
                     yaxis=dict(rangemode="tozero", range=[0, max_val_c5 * 1.25], showgrid=True),
                     legend=dict(yanchor="top", y=0.98, xanchor="right", x=0.98))

    # C6
    df_dec = filtered[filtered['Decade'] >= 1980].groupby('Decade_Str')[
        ['budget', 'profit']].mean().reset_index().sort_values('Decade_Str')
    c6 = go.Figure()
    c6.add_trace(go.Bar(y=df_dec['Decade_Str'], x=df_dec['budget'] / 1e6, name='Avg Budget', orientation='h',
                        marker_color='#94A3B8', marker_line_width=0))
    c6.add_trace(go.Bar(y=df_dec['Decade_Str'], x=df_dec['profit'] / 1e6, name='Avg Profit', orientation='h',
                        marker_color=COLOR_PRIMARY, marker_line_width=0))
    c6.update_layout(barmode='group', bargap=0.2, bargroupgap=0.1,
                     legend=dict(yanchor="top", y=0.85, xanchor="right", x=0.98), xaxis=dict(showgrid=True),
                     yaxis=dict(showgrid=False))

    # C7
    df_scatter = filtered.dropna(subset=['runtime', 'weighted_rating'])
    c7 = go.Figure()
    if not df_scatter.empty:
        c7.add_trace(go.Scatter(x=df_scatter['runtime'], y=df_scatter['weighted_rating'], mode='markers', name='Movies',
                                marker=dict(color=COLOR_PRIMARY, size=5, opacity=0.4, line_width=0),
                                text=df_scatter['title']))
        if len(df_scatter) > 1:
            m, b = np.polyfit(df_scatter['runtime'], df_scatter['weighted_rating'], 1)
            c7.add_trace(
                go.Scatter(x=df_scatter['runtime'], y=m * df_scatter['runtime'] + b, mode='lines', name='Trendline',
                           line=dict(color='#1E40AF', width=2, dash='dot')))

    # C8
    df_bub = filtered[(filtered['profit'] > 0) & (filtered['budget'] > 0) & (filtered['vote_count'] > 100)].copy()
    c8 = go.Figure()
    if not df_bub.empty:
        sizeref = 2.0 * df_bub['budget'].max() / (35 ** 2)
        c8.add_trace(go.Scatter(x=df_bub['vote_count'], y=df_bub['profit'], mode='markers', text=df_bub['title'],
                                marker=dict(size=df_bub['budget'], sizeref=sizeref, sizemode='area',
                                            color=COLOR_PRIMARY, opacity=0.4, line=dict(color='#FFFFFF', width=0.5)),
                                showlegend=False))

    # C9
    c9 = go.Figure(
        go.Histogram(x=filtered['runtime'], xbins=dict(start=40, end=250, size=9), marker_color=COLOR_PRIMARY,
                     marker_line_width=0))
    if not filtered.empty and not filtered['runtime'].isna().all():
        c9.add_vline(x=filtered['runtime'].mean(), line_dash="dash", line_color=COLOR_SECONDARY)

    # C10
    season_order = ['Winter', 'Spring', 'Summer', 'Autumn']
    c10 = go.Figure()
    for season in season_order:
        c10.add_trace(
            go.Box(x=filtered[filtered['Season'] == season]['Season'], y=filtered[filtered['Season'] == season]['ROI'],
                   marker_color=COLOR_PRIMARY, fillcolor='#F8FAFC', line_width=1))
    c10.update_layout(xaxis=dict(categoryorder='array', categoryarray=season_order), yaxis=dict(range=[0, 10]),
                      showlegend=False)

    # C11
    c11 = go.Figure()
    if not filtered.empty and 'performance_status' in filtered.columns:
        c11.add_trace(go.Violin(x=filtered['performance_status'][filtered['performance_status'] == 'Profit'],
                                y=filtered['log_budget'][filtered['performance_status'] == 'Profit'], name='Profit',
                                fillcolor=COLOR_SUCCESS, line_color=COLOR_SUCCESS, meanline_visible=True))
        c11.add_trace(go.Violin(x=filtered['performance_status'][filtered['performance_status'] == 'Loss'],
                                y=filtered['log_budget'][filtered['performance_status'] == 'Loss'], name='Loss',
                                fillcolor=COLOR_DANGER, line_color=COLOR_DANGER, meanline_visible=True))
    c11.update_layout(showlegend=False)

    # C12
    df_ts = filtered[(filtered['release_year'] >= 1990) & (filtered['revenue'] > 0)].groupby('release_year')[
        ['budget', 'revenue']].mean().reset_index()
    c12 = go.Figure()
    c12.add_trace(go.Scatter(x=df_ts['release_year'], y=df_ts['budget'], mode='lines+markers', name='Avg Budget',
                             line=dict(color=COLOR_SECONDARY, width=2)))
    c12.add_trace(go.Scatter(x=df_ts['release_year'], y=df_ts['revenue'], mode='lines+markers', name='Avg Revenue',
                             line=dict(color=COLOR_PRIMARY, width=2)))
    c12.update_layout(legend=dict(yanchor="top", y=0.98, xanchor="left", x=1.02))

    # C13
    df_clean_area = filtered[(filtered['release_year'] >= 1990) & (filtered['release_year'] < 2017)]
    c13 = go.Figure()
    top_4 = ['Action', 'Comedy', 'Drama', 'Adventure']
    colors_area = ['rgba(37, 99, 235, 0.8)', 'rgba(96, 165, 250, 0.8)', 'rgba(147, 197, 253, 0.8)',
                   'rgba(191, 219, 254, 0.8)']
    for i, g in enumerate(top_4):
        if f'genre_{g}' in df_clean_area.columns:
            temp = df_clean_area[df_clean_area[f'genre_{g}'] == 1].groupby('release_year')['profit'].sum().reset_index()
            c13.add_trace(go.Scatter(x=temp['release_year'], y=temp['profit'], mode='lines', name=g, stackgroup='one',
                                     fillcolor=colors_area[i], line_width=0))
    c13.update_layout(legend=dict(yanchor="top", y=0.98, xanchor="right", x=1.135))

    figures = [apply_guidelines(fig) for fig in [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13]]
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

    # DEFAULT: SHOW EVERYTHING SO NO COLUMN IS HIDDEN
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


# Callback explicitly for Custom Explorer graph logic
@app.callback(
    [Output('custom-graph-output', 'figure'),
     Output('custom-chart-title', 'children')],
    [Input('genre-filter', 'value'), Input('language-filter', 'value'), Input('year-filter', 'value'),
     Input('custom-chart-type', 'value'), Input('custom-x-axis', 'value'), Input('custom-y-axis', 'value'),
     Input('custom-group-axis', 'value'), Input('custom-size-axis', 'value')]
)
def update_custom_graph(selected_genres, selected_languages, selected_years, chart_type, x_col, y_col, group_col,
                        size_col):
    if not selected_genres: selected_genres = top_genres
    if not selected_languages: selected_languages = available_languages

    filtered = df[
        (df['main_genre'].isin(selected_genres)) &
        (df['language_group'].isin(selected_languages)) &
        (df['release_year'] >= selected_years[0]) &
        (df['release_year'] <= selected_years[1])
        ]

    fig, title_html = build_dynamic_chart(filtered, chart_type, x_col, y_col, group_col, size_col)

    # --- CLEAN THE TITLE ---
    # Strip HTML tags from the title returned by build_dynamic_chart
    # This prevents raw HTML like <b> or <span> from showing up on the screen
    clean_title = title_html.replace("<b>", "").replace("</b>", "").split("<br>")[0]

    return fig, clean_title


if __name__ == '__main__':
    app.run_server(debug=True)