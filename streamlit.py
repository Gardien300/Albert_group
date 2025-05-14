import streamlit as st
import pandas as pd
from datetime import datetime
import joblib  # Pour charger le modèle de prédiction (si tu as un modèle préentraîné)

# === Chargement des données ===
@st.cache_data
def load_data():
    df = pd.read_csv('/Users/paulin/Desktop/Deploying_ML_project/Albert_group/df_ultimate.csv', parse_dates=['date'])
    return df

df = load_data()

# === Chargement du modèle de prédiction ===
@st.cache_data
def load_model():
    model = joblib.load('/Users/paulin/Desktop/Deploying_ML_project/rf_model.pkl')  # Remplace ce chemin par le chemin réel du modèle
    return model

model = load_model()

# === Utilisation de st.query_params (nouvelle API) ===
params = st.query_params
match_id_selected = params.get("match_id")

# === Page détaillée si un match est sélectionné ===
if match_id_selected:
    match_id_selected = int(match_id_selected)
    match = df[df['match_id'] == match_id_selected].iloc[0]

    st.title(f"{match['home']} 🆚 {match['away']}")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏠 Équipe à domicile")
        st.write(f"**Formation :** {match['formation_home']}")
        st.write(f"**Entraîneur :** {match['coach_home']}")
        st.write(f"**Série de victoires :** {match['home_victory_serie']}")
        st.write(f"**Jours depuis le dernier match :** {match['home_days_since_last_match']}")

    with col2:
        st.subheader("🚗 Équipe à l'extérieur")
        st.write(f"**Formation :** {match['formation_away']}")
        st.write(f"**Entraîneur :** {match['coach_away']}")
        st.write(f"**Série de victoires :** {match['away_victory_serie']}")
        st.write(f"**Jours depuis le dernier match :** {match['away_days_since_last_match']}")

    # === Calcul de la prédiction ===
    features = match[['dob_coach_home', 'trophies_home', 'foundation_home', 'dob_coach_away', 'trophies_away', 'foundation_away', 'venue_capacity', 'temperature', 'wind_speed', 'clouds', 'humidity', 'pressure', 'odd_home', 'odd_draw','odd_away', 'major_league', 'eliminatory_round', 'venue_surface_artificial turf', 'venue_surface_grass', 'home_defenders', 'home_midfielders', 'home_forwards', 'home_goal_scorers', 'away_defenders', 'away_midfielders', 'away_forwards', 'away_goal_scorers', 'home_victory_serie', 'away_victory_serie', 'home_days_since_last_match', 'away_days_since_last_match', 'year', 'month', 'day']].to_frame().T

    # Ajoute un bouton pour prédire
    if st.button("🔮 Prédire l'issue du match"):
        prediction = model.predict(features)  # Calculer la prédiction

        # Afficher le résultat de la prédiction
        if prediction == 0:
            st.write("📍 Résultat attendu : Victoire de l'équipe à domicile")
        elif prediction == 1:
            st.write("📍 Résultat attendu : Victoire de l'équipe à l'extérieur")
        else:
            st.write("📍 Résultat attendu : Match nul")

    if st.button("🔙 Retour"):
        st.query_params.clear()  # Vide les paramètres pour revenir à la page principale

# === Page principale sinon ===
else:
    st.title("🗓️ Matchs de football par date")

    selected_date = st.date_input("Choisissez une date :", value=datetime.today())
    matches_today = df[df['date'].dt.date == selected_date]

    if matches_today.empty:
        st.warning("Aucun match trouvé pour cette date.")
    else:
        grouped = matches_today.groupby('league_name')

        for league, matches in grouped:
            with st.expander(f"⚽ {league} ({len(matches)} matchs)", expanded=True):
                for _, row in matches.iterrows():
                    label = f"{row['home']} vs {row['away']}"
                    html_str = f"""
                    <div style="
                        border: 2px solid #4CAF50;
                        border-radius: 8px;
                        padding: 8px;
                        margin-bottom: 6px;
                        background-color: #f9f9f9;">
                        <a href='?match_id={row['match_id']}' style='text-decoration:none; color:#000; font-weight:bold;'>{label}</a>
                    </div>
                    """
                    st.markdown(html_str, unsafe_allow_html=True)

