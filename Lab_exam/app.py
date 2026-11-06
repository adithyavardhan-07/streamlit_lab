"""
IMDb Movie Analytics Dashboard
Streamlit Practical Examination
================================
Author: Adithya vardhan
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import ast
import os

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="IMDb Movie Analytics Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# Custom Styling (Dark Cinema Theme matching reference UI)
# ---------------------------------------------------------
st.markdown("""
<style>
    /* Dark Theme Backgrounds */
    .stApp {
        background-color: #0b0f19;
        color: #f1f5f9;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid #1e293b;
    }
    
    /* Top Banner Card */
    .hero-banner {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 24px 30px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
    }
    .hero-title {
        font-size: 2.1rem;
        font-weight: 800;
        color: #ffffff;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .hero-subtitle {
        font-size: 1.05rem;
        color: #94a3b8;
        margin-top: 6px;
        font-weight: 400;
    }
    .hero-badge {
        background-color: #f5c518;
        color: #000000;
        font-weight: 900;
        padding: 6px 14px;
        border-radius: 6px;
        font-size: 1.1rem;
        display: inline-block;
        margin-right: 12px;
    }

    /* KPI Cards */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 24px;
    }
    .kpi-card {
        background: #1e293b;
        border-radius: 12px;
        padding: 18px 20px;
        border: 1px solid #334155;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        position: relative;
        overflow: hidden;
    }
    .kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 20px -8px rgba(0, 0, 0, 0.5);
    }
    .kpi-card-cyan { border-top: 4px solid #06b6d4; }
    .kpi-card-green { border-top: 4px solid #10b981; }
    .kpi-card-purple { border-top: 4px solid #8b5cf6; }
    .kpi-card-orange { border-top: 4px solid #f97316; }
    
    .kpi-label {
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94a3b8;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .kpi-value {
        font-size: 2rem;
        font-weight: 800;
        color: #ffffff;
        line-height: 1.1;
    }

    /* Section Headers */
    .section-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #f8fafc;
        margin: 20px 0 14px 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* Card Panels */
    .panel-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }

    /* Filter Tag/Badge */
    .filter-badge {
        display: inline-block;
        background: #0284c7;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 12px;
    }

    /* Movie Result Card */
    .movie-card {
        background: linear-gradient(145deg, #1e293b, #0f172a);
        border: 1px solid #3b82f6;
        border-radius: 12px;
        padding: 16px;
        margin-top: 15px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.3);
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Helper Functions: Robust List Parsing
# ---------------------------------------------------------
def parse_list_col(val):
    """Parses stringified python lists e.g. ['Drama', 'Action'] into real list."""
    if pd.isna(val):
        return []
    if isinstance(val, list):
        return val
    try:
        res = ast.literal_eval(str(val))
        if isinstance(res, list):
            return [str(x).strip() for x in res]
        return [str(res)]
    except Exception:
        # Fallback string split
        cleaned = str(val).strip("[]'\" ")
        return [x.strip().strip("'\"") for x in cleaned.split(',') if x.strip()]

# ---------------------------------------------------------
# Section A – Dataset Loading and Preparation (5 Marks)
# ---------------------------------------------------------
@st.cache_data
def load_movie_data():
    """Loads and preprocesses the IMDb Top 250 Movies Dataset."""
    # Check potential locations for movies.csv
    possible_paths = [
        os.path.join(os.path.dirname(__file__), "movies.csv"),
        "movies.csv",
        r"C:\Users\Jaswanth\Desktop\streamlit_mid\movies.csv",
        r"C:\Users\Jaswanth\Downloads\ToP 250 movies on imdb in 2026.csv",
        r"C:\Users\Jaswanth\.gemini\antigravity\brain\f17eb807-98a8-48b8-b735-90a4fbff99cc\.user_uploaded\media_1793961883207_116cf4f2.csv"
    ]
    
    file_path = None
    for p in possible_paths:
        if os.path.exists(p):
            file_path = p
            break
            
    if file_path is None:
        st.error("Error: movies.csv could not be located. Please place movies.csv in the application directory.")
        st.stop()
        
    df = pd.read_csv(file_path)
    
    # Preprocess list columns
    df['parsed_genres'] = df['genres'].apply(parse_list_col)
    df['primary_genre'] = df['parsed_genres'].apply(lambda x: x[0] if len(x) > 0 else "Unknown")
    df['genre_str'] = df['parsed_genres'].apply(lambda x: ", ".join(x) if len(x) > 0 else "Unknown")
    
    df['parsed_countries'] = df['countriesOfOrigin'].apply(parse_list_col)
    df['primary_country'] = df['parsed_countries'].apply(lambda x: x[0] if len(x) > 0 else "Unknown")
    df['country_str'] = df['parsed_countries'].apply(lambda x: ", ".join(x) if len(x) > 0 else "Unknown")
    
    # Ensure numeric columns
    df['averageRating'] = pd.to_numeric(df['averageRating'], errors='coerce')
    df['numVotes'] = pd.to_numeric(df['numVotes'], errors='coerce').fillna(0).astype(int)
    df['grossWorldwide'] = pd.to_numeric(df['grossWorldwide'], errors='coerce').fillna(0)
    
    return df

# Load the data
df = load_movie_data()

# ---------------------------------------------------------
# Sidebar Section (Navigation & Dataset Information Expander)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">
            <span style="background-color: #f5c518; color: #000; font-weight: 900; padding: 4px 10px; border-radius: 4px; font-size: 1.2rem;">IMDb</span>
            <div style="font-weight: 700; font-size: 1.05rem; line-height: 1.2; color: #fff;">
                Movie Analytics<br><span style="font-size: 0.85rem; color: #94a3b8; font-weight: 400;">Dashboard</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # App Navigation Mode
    nav_selection = st.radio(
        "Navigation",
        options=["📊 Dashboard", "🔍 Movie Explorer", "🔎 Movie Search (Form + Session State)"],
        index=0,
        label_visibility="collapsed"
    )
    
    st.markdown("<hr style='border: 1px solid #1e293b; margin: 18px 0;'>", unsafe_allow_html=True)
    
    # Section A - Question 1 b & c: Dataset Information Expander
    with st.expander("ℹ️ Dataset Information", expanded=True):
        st.markdown(f"""
            **Top 250 Movies on IMDb (2026)**
            
            - **Total Rows:** `{df.shape[0]}`
            - **Total Columns:** `{df.shape[1]}`
            
            This dataset contains curated information regarding the top 250 movies on IMDb, including ratings, vote counts, genres, release dates, and worldwide box office gross.
        """)
        
        st.markdown("**Column Data Types:**")
        dtype_df = pd.DataFrame({"Column": df.columns, "Data Type": [str(t) for t in df.dtypes]})
        st.dataframe(dtype_df.head(8), height=180, use_container_width=True)
        
        # Missing values check (Question 1 c)
        null_counts = df.isnull().sum()
        missing_df = pd.DataFrame({"Column": null_counts.index, "Missing Values": null_counts.values})
        st.markdown(f"**Total Columns with Missing Values:** `{len(missing_df[missing_df['Missing Values'] > 0])}`")

# ---------------------------------------------------------
# Top Header Banner
# ---------------------------------------------------------
st.markdown("""
<div class="hero-banner">
    <div>
        <div style="display: flex; align-items: center; gap: 10px;">
            <span class="hero-badge">IMDb</span>
            <h1 class="hero-title">IMDb Movie Analytics Dashboard</h1>
        </div>
        <div class="hero-subtitle">Explore. Analyze. Discover the Top 250 Rated Movies in Cinema History.</div>
    </div>
    <div style="font-size: 3.5rem; line-height: 1;">🍿🎬</div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Section B – Question 2: Dashboard KPI Metrics (7 Marks)
# ---------------------------------------------------------
total_movies = len(df)                          # Q2 a: Total movies (1 Mark)
avg_rating = df['averageRating'].mean()         # Q2 b: Average IMDb rating (2 Marks)
max_rating = df['averageRating'].max()         # Q2 c: Highest IMDb rating (1 Mark)
total_votes = df['numVotes'].sum()             # Q2 d: Total votes across all movies (2 Marks)

# Q2 e: Display all four KPI metrics in a single row using st.columns(4) (1 Mark)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="kpi-card kpi-card-cyan">
        <div class="kpi-label">🎬 Total Movies</div>
        <div class="kpi-value">{total_movies}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card kpi-card-green">
        <div class="kpi-label">⭐ Average IMDb Rating</div>
        <div class="kpi-value">{avg_rating:.1f}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card kpi-card-purple">
        <div class="kpi-label">🏆 Highest Rating</div>
        <div class="kpi-value">{max_rating:.1f}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card kpi-card-orange">
        <div class="kpi-label">👥 Total Votes</div>
        <div class="kpi-value">{total_votes:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

# Also render Streamlit native st.metric elements inside an expander to ensure 100% adherence to exam hints
with st.expander("🔍 View Native Streamlit Metrics & Dataset Exploration (Section A & B)"):
    mcol1, mcol2, mcol3, mcol4 = st.columns(4)
    mcol1.metric("Total Movies", f"{total_movies}")
    mcol2.metric("Average Rating", f"{avg_rating:.2f}")
    mcol3.metric("Highest Rating", f"{max_rating:.1f}")
    mcol4.metric("Total Votes", f"{total_votes:,}")
    
    st.markdown("#### Section A (a): First 10 Records of Dataset (`df.head(10)`)")
    st.dataframe(df[['primaryTitle', 'averageRating', 'numVotes', 'grossWorldwide', 'genre_str', 'country_str', 'startYear']].head(10), use_container_width=True)
    
    st.markdown("#### Section A (b & c): Column Information & Missing Values Check")
    col_info_df = pd.DataFrame({
        "Column Name": df.columns,
        "Data Type": df.dtypes.astype(str),
        "Missing Values Count": df.isnull().sum()
    }).reset_index(drop=True)
    st.dataframe(col_info_df, use_container_width=True)

st.divider() # Q4 c: Use st.divider() to separate sections (1 Mark)

# ---------------------------------------------------------
# Section B – Question 3 & 4: Visualizations & Layout (11 Marks)
# ---------------------------------------------------------
# Chart 1: Genre analysis (explode genres + value_counts)
exploded_genres = df.explode('parsed_genres')
genre_counts = exploded_genres['parsed_genres'].value_counts().reset_index()
genre_counts.columns = ['Genre', 'Count']

# Genre palette
colors = ['#38bdf8', '#34d399', '#f87171', '#a78bfa', '#fb923c', '#fbbf24', '#e879f9', '#4ade80', '#60a5fa', '#94a3b8']
fig_genre = px.bar(
    genre_counts.head(10),
    x='Genre',
    y='Count',
    text='Count',
    title="<b>Movies by Genre</b>",
    color='Genre',
    color_discrete_sequence=colors
)
fig_genre.update_layout(
    template="plotly_dark",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    xaxis_title="Genre",
    yaxis_title="Count",
    showlegend=False,
    margin=dict(l=20, r=20, t=40, b=20),
    font=dict(color="#94a3b8")
)
fig_genre.update_traces(textposition='outside', marker_line_width=0)

# Chart 2: Histogram of IMDb ratings
fig_hist = px.histogram(
    df,
    x='averageRating',
    nbins=15,
    title="<b>IMDb Rating Distribution</b>",
    color_discrete_sequence=['#3b82f6']
)
fig_hist.update_layout(
    template="plotly_dark",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    xaxis_title="IMDb Rating",
    yaxis_title="Count",
    bargap=0.1,
    margin=dict(l=20, r=20, t=40, b=20),
    font=dict(color="#94a3b8")
)

# Chart 3: Scatter plot Rating vs Number of Votes
fig_scatter = px.scatter(
    df,
    x='averageRating',
    y='numVotes',
    hover_name='primaryTitle',
    title="<b>Rating vs Number of Votes</b>",
    color='averageRating',
    color_continuous_scale="Tealgrn"
)
fig_scatter.update_layout(
    template="plotly_dark",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    xaxis_title="IMDb Rating",
    yaxis_title="Number of Votes",
    coloraxis_showscale=False,
    margin=dict(l=20, r=20, t=40, b=20),
    font=dict(color="#94a3b8")
)

# Chart 4: Top 10 Movies by Worldwide Gross (Bar chart)
top10_gross = df.sort_values(by='grossWorldwide', ascending=False).head(10).copy()
top10_gross['gross_formatted'] = top10_gross['grossWorldwide'].apply(lambda x: f"${x/1e9:.2f}B" if x >= 1e9 else f"${x/1e6:.1f}M")
top10_gross = top10_gross.sort_values(by='grossWorldwide', ascending=True)

fig_gross = px.bar(
    top10_gross,
    x='grossWorldwide',
    y='primaryTitle',
    orientation='h',
    text='gross_formatted',
    title="<b>Top 10 Movies by Worldwide Gross</b>",
    color_discrete_sequence=['#f97316']
)
fig_gross.update_layout(
    template="plotly_dark",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    xaxis_title="Worldwide Gross (USD)",
    yaxis_title="",
    margin=dict(l=20, r=20, t=40, b=20),
    font=dict(color="#94a3b8")
)
fig_gross.update_traces(textposition='inside', marker_line_width=0)

# Q4 a: Use st.tabs() to organize visualizations into separate tabs (1 Mark)
tab1, tab2, tab3, tab4 = st.tabs(["📊 Genre Analysis", "⭐ Rating Analysis", "💰 Gross Collection", "🖥️ All Visualizations Grid"])

with tab1:
    st.plotly_chart(fig_genre, use_container_width=True)

with tab2:
    rcol1, rcol2 = st.columns(2)
    with rcol1:
        st.plotly_chart(fig_hist, use_container_width=True)
    with rcol2:
        st.plotly_chart(fig_scatter, use_container_width=True)

with tab3:
    st.plotly_chart(fig_gross, use_container_width=True)

with tab4:
    # 2x2 Grid exactly matching reference UI screenshot!
    grid_row1_c1, grid_row1_c2 = st.columns(2)
    with grid_row1_c1:
        st.plotly_chart(fig_genre, use_container_width=True)
    with grid_row1_c2:
        st.plotly_chart(fig_hist, use_container_width=True)
        
    grid_row2_c1, grid_row2_c2 = st.columns(2)
    with grid_row2_c1:
        st.plotly_chart(fig_scatter, use_container_width=True)
    with grid_row2_c2:
        st.plotly_chart(fig_gross, use_container_width=True)

# Section A Q1 d: Display appropriate success message (1 Mark)
st.success("✅ Dashboard loaded successfully! Enjoy exploring the top 250 movies on IMDb.")

st.divider()

# ---------------------------------------------------------
# Section C – Question 5 & 6: Interactive Explorer & Form Search
# ---------------------------------------------------------
# Split into 2 main columns: Left for Movie Explorer (65%), Right for Form Search (35%)
explorer_col, search_col = st.columns([1.8, 1.2])

# =========================================================
# Question 5: Interactive Movie Explorer (12 Marks)
# =========================================================
with explorer_col:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 8px; font-size: 1.25rem; font-weight: 700; color: #f8fafc; margin-bottom: 12px;">
            <span>🔽</span> Interactive Movie Explorer
        </div>
    """, unsafe_allow_html=True)
    
    # Initialize Filter State in Session State for Reset Button
    if 'filter_genre' not in st.session_state:
        st.session_state.filter_genre = "All"
    if 'filter_countries' not in st.session_state:
        st.session_state.filter_countries = []
    if 'filter_min_rating' not in st.session_state:
        st.session_state.filter_min_rating = 7.0
    if 'filter_max_rating' not in st.session_state:
        st.session_state.filter_max_rating = 10.0
    if 'filter_min_votes' not in st.session_state:
        st.session_state.filter_min_votes = 100000
    if 'filter_search_title' not in st.session_state:
        st.session_state.filter_search_title = ""
    if 'filter_sort_order' not in st.session_state:
        st.session_state.filter_sort_order = "Descending"

    # Reset Filters Button Handler
    def reset_explorer_filters():
        st.session_state.filter_genre = "All"
        st.session_state.filter_countries = []
        st.session_state.filter_min_rating = 7.0
        st.session_state.filter_max_rating = 10.0
        st.session_state.filter_min_votes = 100000
        st.session_state.filter_search_title = ""
        st.session_state.filter_sort_order = "Descending"

    # Unique Genres and Countries
    all_genres_list = sorted(list(set(exploded_genres['parsed_genres'].dropna().tolist())))
    exploded_countries = df.explode('parsed_countries')
    all_countries_list = sorted(list(set(exploded_countries['parsed_countries'].dropna().tolist())))

    # Filters Row 1: Genre, Countries, Rating Slider
    fcol1, fcol2, fcol3 = st.columns([1, 1.2, 1.3])
    
    with fcol1:
        # Q5 a: Selectbox for Genre (2 Marks)
        selected_genre = st.selectbox(
            "Genre",
            options=["All"] + all_genres_list,
            index=0 if st.session_state.filter_genre == "All" else (all_genres_list.index(st.session_state.filter_genre) + 1 if st.session_state.filter_genre in all_genres_list else 0),
            key="filter_genre"
        )
        
    with fcol2:
        # Q5 b: Multiselect for Countries (2 Marks)
        selected_countries = st.multiselect(
            "Countries",
            options=all_countries_list,
            default=st.session_state.filter_countries,
            key="filter_countries"
        )
        
    with fcol3:
        # Q5 c: Slider for Rating (2 Marks)
        rating_range = st.slider(
            "IMDb Rating Range",
            min_value=7.0,
            max_value=10.0,
            value=(st.session_state.filter_min_rating, st.session_state.filter_max_rating),
            step=0.1
        )
        st.session_state.filter_min_rating, st.session_state.filter_max_rating = rating_range

    # Filters Row 2: Min Votes, Search Title, Sort Order
    fcol4, fcol5, fcol6 = st.columns([1, 1.2, 1.1])
    
    with fcol4:
        # Q5 d: Number Input for Min Votes (1 Mark)
        min_votes_input = st.number_input(
            "Min Votes",
            min_value=0,
            max_value=int(df['numVotes'].max()),
            value=st.session_state.filter_min_votes,
            step=50000,
            key="filter_min_votes"
        )
        
    with fcol5:
        # Q5 e: Text Input for Search Title (1 Mark)
        search_title_input = st.text_input(
            "Search Title",
            value=st.session_state.filter_search_title,
            placeholder="Enter movie title...",
            key="filter_search_title"
        )
        
    with fcol6:
        # Q5 f: Radio Button for Sort Order (1 Mark)
        sort_order = st.radio(
            "Sort Order",
            options=["Descending", "Ascending"],
            index=0 if st.session_state.filter_sort_order == "Descending" else 1,
            horizontal=True,
            key="filter_sort_order"
        )

    # Filtering Logic (Cumulative filtering on copy of DataFrame)
    filtered_df = df.copy()

    # Apply Genre condition
    if selected_genre != "All":
        filtered_df = filtered_df[filtered_df['parsed_genres'].apply(lambda genres: selected_genre in genres)]

    # Apply Countries condition
    if selected_countries:
        filtered_df = filtered_df[filtered_df['parsed_countries'].apply(lambda countries: any(c in countries for c in selected_countries))]

    # Apply Rating condition
    filtered_df = filtered_df[
        (filtered_df['averageRating'] >= rating_range[0]) & 
        (filtered_df['averageRating'] <= rating_range[1])
    ]

    # Apply Min Votes condition
    filtered_df = filtered_df[filtered_df['numVotes'] >= min_votes_input]

    # Apply Title Search condition
    if search_title_input.strip():
        filtered_df = filtered_df[filtered_df['primaryTitle'].str.contains(search_title_input.strip(), case=False, na=False)]

    # Apply Sorting
    is_ascending = (sort_order == "Ascending")
    filtered_df = filtered_df.sort_values(by='averageRating', ascending=is_ascending)

    # Q5 g: Display total number of movies remaining & Q5 h: Reset Button (3 Marks)
    bcol1, bcol2 = st.columns([1, 1])
    with bcol1:
        st.markdown(f"""
            <div style="background-color: #0284c7; color: white; display: inline-block; padding: 6px 14px; border-radius: 6px; font-weight: 700; font-size: 0.9rem; margin-top: 6px;">
                Filtered Movies: {len(filtered_df)}
            </div>
        """, unsafe_allow_html=True)
    with bcol2:
        st.button("🔄 Reset Filters", on_click=reset_explorer_filters, use_container_width=True)

    # Q5 h: Display final filtered DataFrame using st.dataframe()
    display_df = filtered_df[['primaryTitle', 'genre_str', 'country_str', 'averageRating', 'numVotes', 'grossWorldwide']].copy()
    display_df.columns = ['Title', 'Genre', 'Country', 'IMDb Rating', 'Votes', 'Worldwide Gross']
    display_df['Worldwide Gross'] = display_df['Worldwide Gross'].apply(lambda x: f"${x/1e9:.2f}B" if x >= 1e9 else (f"${x/1e6:.1f}M" if x >= 1e6 else f"${x:,.0f}"))
    display_df['Votes'] = display_df['Votes'].apply(lambda x: f"{x:,}")
    display_df = display_df.reset_index(drop=True)
    display_df.index = display_df.index + 1
    
    st.dataframe(display_df, height=340, use_container_width=True)

# =========================================================
# Question 6: Session State and Form Handling (10 Marks)
# =========================================================
with search_col:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 8px; font-size: 1.25rem; font-weight: 700; color: #f8fafc; margin-bottom: 12px;">
            <span>🔍</span> Movie Search (Form + Session State)
        </div>
    """, unsafe_allow_html=True)

    # Q6 a: Initialize session state variable (2 Marks)
    if 'selected_movie' not in st.session_state:
        # Prepopulate with a default movie matching reference screenshot (Inception)
        default_match = df[df['primaryTitle'] == 'Inception']
        st.session_state.selected_movie = default_match.iloc[0].to_dict() if len(default_match) > 0 else None

    # Q6 b: Create a form using st.form() (3 Marks)
    with st.form("movie_search_form"):
        form_title = st.text_input("Movie Title", value="Inception", placeholder="e.g. Inception, The Dark Knight")
        form_genre = st.selectbox("Preferred Genre", options=["Any"] + all_genres_list, index=0)
        form_rating = st.slider("Minimum IMDb Rating", min_value=0.0, max_value=10.0, value=8.0, step=0.1)
        
        # Q6 c: Submit button inside form (2 Marks)
        submitted = st.form_submit_button("🔍 Search Movie", use_container_width=True)
        
        if submitted:
            # Process preferences only after submission
            search_query = df.copy()
            
            if form_title.strip():
                search_query = search_query[search_query['primaryTitle'].str.contains(form_title.strip(), case=False, na=False)]
            
            if form_genre != "Any":
                search_query = search_query[search_query['parsed_genres'].apply(lambda g: form_genre in g)]
                
            search_query = search_query[search_query['averageRating'] >= form_rating]
            
            if len(search_query) > 0:
                # Store selected movie in session state (Q6 a & d)
                st.session_state.selected_movie = search_query.iloc[0].to_dict()
                st.session_state.search_status = "success"
                st.session_state.search_msg = f"Movie found successfully! ({len(search_query)} matching movies found)"
            else:
                st.session_state.selected_movie = None
                st.session_state.search_status = "not_found"
                st.session_state.search_msg = "No matching movie found with the selected preferences. Try lowering the rating or clearing filters."

    # Q6 d & e: Display movie information & appropriate success/info message (3 Marks)
    if st.session_state.selected_movie:
        movie = st.session_state.selected_movie
        st.success("✅ Movie found successfully!")
        
        poster_url = movie.get('primaryImage', '')
        poster_html = f"""<img src="{poster_url}" style="width: 75px; height: 110px; object-fit: cover; border-radius: 6px; box-shadow: 0 4px 8px rgba(0,0,0,0.5);">""" if poster_url and str(poster_url) != 'nan' else """<div style="width: 75px; height: 110px; background: #334155; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 1.8rem;">🎬</div>"""
        
        st.markdown(f"""
            <div class="movie-card">
                <div style="display: flex; gap: 16px; align-items: flex-start;">
                    {poster_html}
                    <div style="flex: 1;">
                        <div style="font-size: 1.25rem; font-weight: 800; color: #ffffff; margin-bottom: 4px;">{movie.get('primaryTitle', 'N/A')}</div>
                        <div style="font-size: 0.9rem; color: #38bdf8; font-weight: 600; margin-bottom: 6px;">
                            🎭 Genre: {movie.get('genre_str', 'N/A')}
                        </div>
                        <div style="display: flex; gap: 14px; font-size: 0.85rem; color: #cbd5e1; margin-bottom: 8px;">
                            <span>⭐ Rating: <b style="color: #facc15;">{movie.get('averageRating', 'N/A')}</b></span>
                            <span>👥 Votes: <b>{int(movie.get('numVotes', 0)):,}</b></span>
                        </div>
                        <div style="font-size: 0.82rem; color: #94a3b8; line-height: 1.4;">
                            {str(movie.get('description', ''))[:160]}...
                        </div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info("ℹ️ No movie selected. Use the search form above to find and explore movie details.")

# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 0.85rem; margin-top: 40px; padding: 20px 0; border-top: 1px solid #1e293b;">
    IMDb Top 250 Movies Analytics Dashboard • Developed with Streamlit, Pandas & Plotly • Exam Practical 2026
</div>
""", unsafe_allow_html=True)
