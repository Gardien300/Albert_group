import streamlit as st
import pandas as pd
from datetime import datetime

@st.cache_data
def load_data():
    df = pd.read_csv('/Users/paulin/Desktop/Deploying_ML_project/Albert_group/df_ultimate.csv', parse_dates=['date'])
    return df

def app():
    df = load_data()
    st.title("Historique des matchs - calendrier hebdomadaire")

    # Création de la colonne année-semaine
    df['year_week'] = df['date'].dt.strftime('%Y-%U')
    
    def week_str_to_date(week_str):
        year, week = week_str.split('-')
        return datetime.strptime(f'{year} {int(week)} 1', '%Y %U %w')
    
    # Liste des semaines disponibles et format affichage
    unique_weeks = sorted(df['year_week'].unique())
    weeks_display = [f"Semaine du {week_str_to_date(w).strftime('%d %B %Y')}" for w in unique_weeks]
    
    selected_week_display = st.selectbox("Choisissez une semaine :", weeks_display)
    selected_week = unique_weeks[weeks_display.index(selected_week_display)]
    
    df_selected = df[df['year_week'] == selected_week].sort_values('date')
    grouped_dates = df_selected.groupby(df_selected['date'].dt.date)
    
    for date, matches_day in grouped_dates:
        st.write(f"### {date.strftime('%A %d %B %Y')}")
        grouped_leagues = matches_day.groupby('league_name')
        for league, matches_league in grouped_leagues:
            with st.expander(f"{league} ({len(matches_league)} matchs)", expanded=False):
                for _, row in matches_league.iterrows():
                    st.write(f"- {row['home']} vs {row['away']}")

