import streamlit as st
import app_prediction2
import app_calendar
from predict_league_ranking import show_league_ranking

st.sidebar.title("Navigation")
page = st.sidebar.radio("Choisissez une page :", ["Prédiction Match", "Calendrier Semaine", "Classement par League"])

if page == "Prédiction Match":
    app_prediction2.app()
elif page == "Calendrier Semaine":
    app_calendar.app()
elif page == "Classement par League":
    show_league_ranking()