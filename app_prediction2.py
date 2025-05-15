import streamlit as st
import pandas as pd
import numpy as np
import random
import joblib
from datetime import datetime, timedelta

# === Chargement des données historiques ===
@st.cache_data
def load_data():
    df = pd.read_csv('/Users/paulin/Desktop/Deploying_ML_project/Albert_group/df_ultimate.csv', parse_dates=['date'])
    return df

def app():
    df = load_data()

    # === Chargement du modèle ===
    model = joblib.load("/Users/paulin/Desktop/Deploying_ML_project/rf_model.pkl")

    # === Générer une ligne de match aléatoire ===
    def generate_random_match(df):
        row = df.sample(1).iloc[0].copy()
        features_to_keep = [
            'round', 'home', 'formation_home', 'coach_home', 'dob_coach_home',
            'trophies_home', 'foundation_home', 'away', 'formation_away', 'coach_away',
            'dob_coach_away', 'trophies_away', 'foundation_away', 'venue_city',
            'venue_capacity', 'league', 'temperature', 'wind_speed', 'clouds', 'humidity',
            'pressure', 'league_name', 'league_country', 'major_league',
            'eliminatory_round', 'venue_surface_artificial turf', 'venue_surface_grass',
            'home_defenders', 'home_midfielders', 'home_forwards', 'home_goal_scorers',
            'away_defenders', 'away_midfielders', 'away_forwards', 'away_goal_scorers',
            'home_victory_serie', 'away_victory_serie', 'home_days_since_last_match',
            'away_days_since_last_match', 'odd_home', 'odd_away', 'odd_draw'
        ]
        new_match = row[features_to_keep]

        max_date = df['date'].max()
        random_days = random.randint(1, 100)
        new_match['date'] = max_date + timedelta(days=random_days)
        new_match['year'] = new_match['date'].year
        new_match['month'] = new_match['date'].month
        new_match['day'] = new_match['date'].day
        return new_match

    # === Titre ===
    st.title("🎲 Générateur de match et prédiction")

    # === Choix entre aléatoire ou manuel ===
    mode = st.radio("Choisissez le mode d'entrée des données :", ["🔄 Génération aléatoire", "✍️ Saisie manuelle"])

    if mode == "🔄 Génération aléatoire":
        if st.button("🎰 Générer un match aléatoire"):
            match = generate_random_match(df)
            st.session_state.generated_match = match

    elif mode == "✍️ Saisie manuelle":
        st.subheader("Remplir manuellement les caractéristiques du match")

        col1, col2 = st.columns(2)
        with col1:
            home = st.text_input("Équipe à domicile")
            formation_home = st.text_input("Formation à domicile")
            coach_home = st.text_input("Coach à domicile")
            dob_coach_home = st.number_input("Année de naissance du coach à domicile", 1940, 2005, 1970)
            trophies_home = st.number_input("Trophées domicile", 0, 50, 5)
            foundation_home = st.number_input("Année de fondation domicile", 1850, 2025, 1900)
            odd_home = st.number_input("Cote domicile", 1.0, 10.0, 2.5)

        with col2:
            away = st.text_input("Équipe à l'extérieur")
            formation_away = st.text_input("Formation à l'extérieur")
            coach_away = st.text_input("Coach à l'extérieur")
            dob_coach_away = st.number_input("Année de naissance du coach à l'extérieur", 1940, 2005, 1970)
            trophies_away = st.number_input("Trophées extérieur", 0, 50, 5)
            foundation_away = st.number_input("Année de fondation extérieur", 1850, 2025, 1900)
            odd_away = st.number_input("Cote extérieur", 1.0, 10.0, 2.5)
            odd_draw = st.number_input("Cote match nul", 1.0, 10.0, 3.0)

        temperature = st.slider("Température (°C)", -10, 40, 20)
        wind_speed = st.slider("Vitesse du vent (km/h)", 0, 100, 10)
        clouds = st.slider("Couverture nuageuse (%)", 0, 100, 50)
        humidity = st.slider("Humidité (%)", 0, 100, 60)
        pressure = st.slider("Pression (hPa)", 900, 1100, 1010)

        date_input = st.date_input("Date du match", min_value=df['date'].max() + timedelta(days=1))

        match = {
            'home': home, 'formation_home': formation_home, 'coach_home': coach_home, 'dob_coach_home': dob_coach_home,
            'trophies_home': trophies_home, 'foundation_home': foundation_home, 'away': away,
            'formation_away': formation_away, 'coach_away': coach_away, 'dob_coach_away': dob_coach_away,
            'trophies_away': trophies_away, 'foundation_away': foundation_away, 'venue_city': 'Paris',
            'venue_capacity': 50000, 'temperature': temperature, 'wind_speed': wind_speed,
            'clouds': clouds, 'humidity': humidity, 'pressure': pressure, 'odd_home': odd_home,
            'odd_draw': odd_draw, 'odd_away': odd_away, 'major_league': 1, 'eliminatory_round': 0,
            'venue_surface_artificial turf': 0, 'venue_surface_grass': 1, 'home_defenders': 4,
            'home_midfielders': 3, 'home_forwards': 3, 'home_goal_scorers': 2, 'away_defenders': 4,
            'away_midfielders': 3, 'away_forwards': 3, 'away_goal_scorers': 2, 'home_victory_serie': 1,
            'away_victory_serie': 0, 'home_days_since_last_match': 5, 'away_days_since_last_match': 6,
            'date': pd.to_datetime(date_input), 'year': date_input.year, 'month': date_input.month, 'day': date_input.day
        }

        st.session_state.generated_match = pd.Series(match)

    # === Affichage du match généré ===
    if "generated_match" in st.session_state:
        match = st.session_state.generated_match
        st.subheader(f"{match['home']} 🆚 {match['away']} ({match['date'].date()})")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"🏠 **Équipe à domicile :** {match['home']}")
            st.markdown(f"🎯 Formation : {match['formation_home']}")
            st.markdown(f"👨‍🏫 Entraîneur : {match['coach_home']}")
            st.markdown(f"🏙️ Ville : {match['venue_city']}")

        with col2:
            st.markdown(f"🚗 **Équipe à l'extérieur :** {match['away']}")
            st.markdown(f"🎯 Formation : {match['formation_away']}")
            st.markdown(f"👨‍🏫 Entraîneur : {match['coach_away']}")
            st.markdown(f"📊 Cotes — Domicile : {match['odd_home']} / Nul : {match['odd_draw']} / Extérieur : {match['odd_away']}")

        st.markdown("---")
        with st.expander("📦 Voir toutes les données simulées (debug/dev)"):
            st.dataframe(match)

        if st.button("🔮 Prédire l'issue"):
            feature_cols = ['dob_coach_home', 'trophies_home', 'foundation_home', 'dob_coach_away',
                            'trophies_away', 'foundation_away', 'venue_capacity', 'temperature',
                            'wind_speed', 'clouds', 'humidity', 'pressure', 'odd_home', 'odd_draw',
                            'odd_away', 'major_league', 'eliminatory_round',
                            'venue_surface_artificial turf', 'venue_surface_grass', 'home_defenders',
                            'home_midfielders', 'home_forwards', 'home_goal_scorers', 'away_defenders',
                            'away_midfielders', 'away_forwards', 'away_goal_scorers', 'home_victory_serie',
                            'away_victory_serie', 'home_days_since_last_match', 'away_days_since_last_match',
                            'year', 'month', 'day']

            X_pred = pd.DataFrame([match])[feature_cols]
            pred = model.predict(X_pred)[0]
            label = match['home'] if pred == 'home_winner' else match['away'] if pred == 'away_winner' else "match nul"

            st.markdown(
                f"""
            <div style='border: 2px solid white; padding: 1rem; border-radius: 10px; background-color: #0e1117; color: white; text-align: center;'>
                🏆 <strong>Le gagnant du match sera : {label}</strong>
            </div>
            """,
                unsafe_allow_html=True
            )
            
            proba = model.predict_proba(X_pred)[0]
            classes = model.classes_

            # Mapping proba
            proba_dict = dict(zip(classes, proba))
            home_team = match['home']
            away_team = match['away']

            home_proba = proba_dict.get("home_winner", 0)
            draw_proba = proba_dict.get("draw", 0)
            away_proba = proba_dict.get("away_winner", 0)

            # ---- Affichage Streamlit ----
            st.markdown("### 🎯 Confiance du modèle")

            col1, col2, col3 = st.columns([1, 1, 1])

            with col1:
                st.markdown(f"**{home_team} (home)**")
                st.markdown(f"<h2 style='color:white;'>{home_proba*100:.1f} %</h2>", unsafe_allow_html=True)

            with col2:
                st.markdown("**Match nul**")
                st.markdown(f"<h2 style='color:white;'>{draw_proba*100:.1f} %</h2>", unsafe_allow_html=True)

            with col3:
                st.markdown(f"**{away_team} (away)**")
                st.markdown(f"<h2 style='color:white;'>{away_proba*100:.1f} %</h2>", unsafe_allow_html=True)

            # ---- Barre de probabilité à 3 segments ----
            total = home_proba + draw_proba + away_proba
            home_ratio = home_proba / total
            draw_ratio = draw_proba / total
            away_ratio = away_proba / total

            st.markdown(f"""
            <div style='background-color:#1e1e1e; border-radius:8px; height:5px; width:100%; display:flex; overflow:hidden; margin-top:10px;'>
                <div style='width:{home_ratio*100:.1f}%; background-color:#2563eb;'></div>
                <div style='width:{draw_ratio*100:.1f}%; background-color:#FFFFFF;'></div>
                <div style='width:{away_ratio*100:.1f}%; background-color:#6B21A8;'></div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### 🧠 Importance globale des caractéristiques")
            importances = model.feature_importances_
            feature_names = model.feature_names_in_
            importance_df = pd.Series(importances, index=feature_names).sort_values()
            st.bar_chart(importance_df)
            
            top_features = sorted(zip(feature_cols, importances), key=lambda x: x[1], reverse=True)[:3]
            top_features_names = ", ".join([f[0] for f in top_features])


            st.markdown(f"<p style='font-size:13px;'>ℹ️ Notre algorithme de prédiction se base principalement sur : <b>{top_features_names}</b>.</p>", unsafe_allow_html=True)
