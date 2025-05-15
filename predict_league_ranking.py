import streamlit as st
import pandas as pd
import os
import xgboost as xgb
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import mean_absolute_error

# -----------------------------
# PARAMÈTRES
# -----------------------------
MODEL_DIR = "models_by_league"
FEATURES = [
    "avg_goals_scored", "avg_goals_conceded",
    "avg_coach_age", "max_trophies",
    "avg_club_age", "avg_stadium_capacity"
]

@st.cache_data
def load_data():
    df = pd.read_csv("/Users/paulin/Desktop/Deploying_ML_project/Albert_group/team_features_ready.csv")
    df["wins"] = pd.to_numeric(df["wins"], errors="coerce")
    df = df.dropna(subset=FEATURES + ["wins", "winrate", "matches"])
    df = df[df["matches"] >= 3]
    return df

@st.cache_resource
def load_model(league_name):
    file_name = league_name.replace("/", "-") + ".json"
    model_path = os.path.join(MODEL_DIR, file_name)
    if not os.path.exists(model_path):
        return None
    model = xgb.XGBRegressor()
    model.load_model(model_path)
    return model

def show_league_ranking():
    df = load_data()
    st.title("📊 Classement par ligue")

    selected_league = st.selectbox("Sélectionnez une ligue :", sorted(df["league"].unique()))
    model = load_model(selected_league)

    if model is None:
        st.error(f"Aucun modèle trouvé pour la ligue : {selected_league}")
        return

    league_df = df[df["league"] == selected_league].copy()
    X = league_df[FEATURES]
    preds = model.predict(X)
    preds = np.clip(preds, 0, 1)
    league_df["predicted_winrate"] = preds
    league_df = league_df.sort_values(by="predicted_winrate", ascending=False)

    st.subheader(f"🏆 Classement prédit pour {selected_league}")
    st.dataframe(league_df[["team", "matches", "wins", "winrate", "predicted_winrate"]])

    # Comparaison
    st.markdown("### 📊 Comparaison Winrate Réel vs Prédit")
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.scatterplot(x="winrate", y="predicted_winrate", data=league_df, ax=ax)
    ax.plot([0, 1], [0, 1], linestyle="--", color="gray")
    ax.set_xlabel("Winrate réel")
    ax.set_ylabel("Winrate prédit")
    st.pyplot(fig)

    # MAE
    mae = mean_absolute_error(league_df["winrate"], league_df["predicted_winrate"])
    st.metric("📏 MAE (Erreur absolue moyenne)", f"{mae:.4f}")

    # Importance des features
    try:
        booster = model.get_booster()
        scores = booster.get_score(importance_type='gain')
        scores = pd.Series(scores).sort_values(ascending=False)

        st.markdown("### 🔠 Importance des Caractéristiques")
        fig2, ax2 = plt.subplots()
        scores.plot(kind="barh", ax=ax2)
        ax2.invert_yaxis()
        st.pyplot(fig2)
    except:
        st.warning("Impossible d'afficher l'importance des caractéristiques pour ce modèle.")