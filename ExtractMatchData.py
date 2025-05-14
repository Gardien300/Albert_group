import requests
import pandas as pd
import time
import numpy as np
import sys
from datetime import date
from datetime import datetime
from joblib import Memory

API_TOKEN = "HrrfH7B0VdIHpsHU3SolfjsoWY6b34xpUbTwDAWHanGMfBPXm20QzhSQoQrJ"

# FONCTIONS POUR LA FLUIDITÉ DU CODE
# fonction permettant de pauser l'extraction par call API lorsque notre limite gratuite est atteinte (3000 calls par heure sur Sportmonks)

def pause(data):
    if data["rate_limit"]["remaining"] == 0:
        seconds = data["rate_limit"]["resets_in_seconds"]
        
        print(f"\n📛 Limite atteinte. Pause pendant {seconds} secondes :")

        for remaining in range(seconds, 0, -1):
            sys.stdout.write(f"\r⏳ Reprise dans {remaining} seconde(s)...")
            sys.stdout.flush()
            time.sleep(1)

        print("\n✅ Reprise du script.")


# ces deux fonctions permettent de faire des calls API "sûr" qui ne font pas crash le code lorsque les valeurs extraites sont Nan

def safe_get(d, key, default=np.nan):
    return d.get(key, default) if isinstance(d, dict) else default

def safe_index(lst, index, key, default=np.nan):
    if isinstance(lst, list) and len(lst) > index and isinstance(lst[index], dict):
        return lst[index].get(key, default)
    return default


# fonction permettant de garder en mémoire les éléments déjà extraits et donc de ne pas recommencer tout le code à chaque test en cas d'erreur

memory = Memory(location='cache_api', verbose=0)

@memory.cache
def get_api_data(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


# EXTRACTION DES DONNÉES UTILES AU PROJET
# On extrait tous les matchs de foot de la saison 2024-2025 qui sont identifiés par deux id : id de league et id de saison

def leagues_identification(target_season_name="2024/2025"): 
    leagues = []
    seasons = []
    all_leagues = []
    page = 1

    while True:
        url = f"https://api.sportmonks.com/v3/football/seasons?api_token={API_TOKEN}&per_page=50&page={page}"
        leagues_data = get_api_data(url)

        if "data" not in leagues_data:
            print("Erreur ou format inattendu :", data)
            break

        for season in leagues_data["data"]:
            all_leagues.append(season["league_id"])
            if season["name"]==target_season_name: 
                seasons.append(season["id"])
                leagues.append(season["league_id"])

        if not leagues_data["pagination"]["has_more"]:
            break

        page += 1
        
        pause(leagues_data)
        
    print("Nombre de pages total :",page)
    print("Tous les identifiants des leagues :", leagues)
    print("Tous les identifiants des saisons :", seasons)
    print("Nombre de league contre nombre de leagues total :",len( leagues), "/", len(all_leagues))
    
    return leagues, seasons


# On extrait nos data pour chaque match de cette saison

def matchs():
    matchs = []
    page=1
    leagues, seasons = leagues_identification()
    leagues = ", ".join(str(x) for x in leagues)
    seasons = ", ".join(str(x) for x in seasons)
    
    while True:
        url = f"https://api.sportmonks.com/v3/football/fixtures?api_token={API_TOKEN}&per_page=50&page={page}&include=league;scores;venue;stage;participants.trophies;weatherReport;league;formations;coaches&filters=fixtureLeagues:{leagues};fixtureSeasons:{seasons};fixtureStates:5"
        matchs_data = get_api_data(url)
        
        
        if "data" not in matchs_data:
            print("Erreur ou format inattendu :", matchs_data)
            break
        
        else : 
            print("resultat trouvé page : ", page)

        for match in matchs_data.get("data", []):
            
            id_home = match["participants"][0]["id"]
            home = match["participants"][0]["name"]
            id_away = match["participants"][1]["id"]
            away = match["participants"][1]["name"]     

            # les équipes sont toujours données dans l'ordre suivant : home puis away
            
            formations_dict = {form["participant_id"]: form["formation"] for form in match["formations"]}
            coaches_dict = {coach["meta"]["participant_id"]: (coach.get("name", "nom"),coach.get("date_of_birth", "date_naiss")) for coach in match["coaches"]}
            participant_dict = {participant["id"]: (participant.get("trophies", "trophés"),participant.get("founded", "fondation"), participant.get("meta", "meta")) for participant in match["participants"]}
            
            coach1_name, coach1_birth = coaches_dict.get(id_home, ("nom", "date_naiss"))
            coach2_name, coach2_birth = coaches_dict.get(id_away, ("nom", "date_naiss"))
            trophies1, foundation1, meta1 = participant_dict.get(id_home, ("trophés", "fondation", "meta"))
            trophies2, foundation2, meta2 = participant_dict.get(id_away, ("trophés", "fondation", "meta"))
            
            
            matchs.append({
                "match_id": safe_get(match, "id"),
                "league_id": safe_get(match, "league_id"),
                "state_id": safe_get(match, "state_id"),
                "venue_id": safe_get(match, "venue_id"),
                "starting_at": safe_get(match, "starting_at"),
                "result_info": safe_get(match, "result_info"),
                "round": safe_get(match.get("stage"), "name"),
                "home": home,
                "home_winner": meta1["winner"],
                "formation_home": formations_dict.get(id_home, "Inconnue"),
                "coach_home": coach1_name,
                "dob_coach_home": coach1_birth,
                "trophies_home": len(trophies1),
                "foundation_home": foundation1,
                "away":away,
                "away_winner": meta2["winner"],
                "formation_away": formations_dict.get(id_away, "Inconnue"),
                "coach_away": coach2_name,
                "dob_coach_away": coach2_birth,
                "trophies_away": len(trophies2),
                "foundation_away": foundation2, 
                "venue_city": safe_get(match.get("venue"), "city_name"),
                "venue_capacity": safe_get(match.get("venue"), "capacity"),
                "venue_surface": safe_get(match.get("venue"), "surface"),
                "league": safe_get(match.get("league"), "name"),
                "league_type": safe_get(match.get("league"), "type"),
                "temperature": safe_get(safe_get(match.get("weatherreport"), "temperature"), "day"),
                "wind_speed": safe_get(safe_get(match.get("weatherreport"), "wind"), "speed"),
                "clouds": safe_get(match.get("weatherreport"), "clouds"),
                "humidity": safe_get(match.get("weatherreport"), "humidity"),
                "pressure": safe_get(match.get("weatherreport"), "pressure"),
            })
        
        if not matchs_data["pagination"]["has_more"]:
            break

        page += 1
        
        pause(matchs_data)
                
    print(page)
    print(matchs_data)
        
    df_matchs = pd.DataFrame(matchs)
        
    return df_matchs


# fonction qui trouve, pour chaque match extrait, les côtes de toutes les issues (match nul, victoire à domicile, victoire à l'éxterieur)

def odds(df):
    all_odds = []

    for fixture in df["match_id"]: 
        url = f"https://api.sportmonks.com/v3/football/odds/pre-match/fixtures/{fixture}/bookmakers/2?api_token={API_TOKEN}&include=market&filters=markets:1"
        try : 
            odds_data = get_api_data(url)
        except ConnectionError: 
            time.sleep(1)
            odds_data = get_api_data(url)
        
        
        # Dictionnaire pour stocker les 3 cotes d'un même match
        match_odds = {"match_id": fixture, "Home": None, "Draw": None, "Away": None}
        
        for odds_type in odds_data.get("data", []):
            label = odds_type.get("label")
            value = odds_type.get("value")
            if label in match_odds:
                match_odds[label] = value
        
        all_odds.append(match_odds)
        
        pause(odds_data)
    
    return pd.DataFrame(all_odds)


# ÉXÉCUTION DU CODE - EXTRACTION DES DONNÉES ET FORMATAGE
df_matchs = matchs() # dataset des features globales
df_odds = odds() # dataset des côtes de chaque match

df_matchs["draw"] = (df_matchs["away_winner"] == False) & (df_matchs["home_winner"] == False)

# merge des deux datasets
df_odds.rename(columns={"Home":"odd_home", "Draw": "odd_draw", "Away": "odd_away"})
df_matchs = pd.merge(df_matchs, df_odds, on="match_id", how="left")

# formatage des dates
df_matchs.rename(columns={"starting_at":"date"}, inplace=True)

dates = ["date"]
date_coaches = ["dob_coach_home", "dob_coach_away"] 
for col in dates: 
    df_matchs[col] = pd.to_datetime(df_matchs[col], format="%Y-%m-%d %H:%M:%S", errors="coerce")
for col in date_coaches:
    df_matchs[col] = pd.to_datetime(df_matchs[col], format="%Y-%m-%d", errors="coerce")


# classer les leagues pour savoir leur "renommée" (leur importance) - si elles sont considérées comme des leagues majeures 
major_leagues = {
    'Premier League': True,
    'La Liga': True,
    'Bundesliga': True,
    'Serie A': True,
    'Ligue 1': True,
    'Champions League': True,
    'Europa League': True,
    'FA Cup': True,
    'Coppa Italia': True,
    'Carabao Cup': True,
    'Europa Conference League': True,  # médiatisée malgré son niveau

    'Ekstraklasa': False,
    '1. HNL': False,
    'Superliga': False,
    'Pro League': False,
    'Super League': False,
    'Eredivisie': False,
    'Championship': False,
    'La Liga 2': False,
    'Premiership': False,
    'Admiral Bundesliga': False,
    'Serie B': False,
    'Liga Portugal': False,
    'Super Lig': False,
    'Copa Del Rey': False
}
df_matchs["major_league"] = df_matchs["league"].map(major_leagues)


# classer les rounds pour savoir si ils sont à élimination directe (et donc plus importants)
phases_dict = {
    "Regular Season": False,
    "1st Qualifying Round": True,
    "2nd Qualifying Round": True,
    "1st Round": True,
    "1st Phase": False,
    "Preliminary Round": True,
    "Extra Preliminary Round": True,
    "Quarter-finals": True,
    "Round of 16": True,
    "2nd Round": True,
    "Semi-finals": True,
    "3rd Qualifying Round": True,
    "Extra Preliminary Round Replays": True,
    "Play-offs": True,
    "Preliminary Round Replays": True,
    "1st Round Qualifying": True,
    "3rd Round": True,
    "League Stage": False,
    "1st Round Qualifying Replays": True,
    "2nd Round Qualifying": True,
    "2nd Round Qualifying Replays": True,
    "3rd Round Qualifying": True,
    "3rd Round Qualifying Replays": True,
    "4th Round Qualifying": True,
    "4th Round Qualifying Replays": True,
    "Round of 32": True,
    "Knockout Round Play-offs": True,
    "4th Round": True,
    "5th Round": True,
    "Final": True,
    "Championship Round": False,
    "Relegation Round": False,
    "Conference League Play-off Group": False,
    "2nd Phase": False
}
df_matchs["eliminatory_round"] = df_matchs["round"].map(phases_dict)

# One Hot Encoder les valeurs possibles de la surface du stade du match
df_matchs = pd.get_dummies(df_matchs, columns=['venue_surface'])


# conversion des compositions des équipes en données exploitables (4 colonnes - une pour chaque "ligne" de joueur)
def extract_positions(formation):
    if not isinstance(formation, str) or formation.strip() == "":
        return 0, 0, 0, 0
    
    parts = formation.strip().split('-')
    try:
        defenders = int(parts[0]) if len(parts) > 0 else 0
        midfielders = int(parts[1]) if len(parts) > 1 else 0
        forwards = int(parts[2]) if len(parts) > 2 else 0
        goal_scorers = int(parts[3]) if len(parts) > 3 else forwards
    except ValueError:
        return 0, 0, 0, 0  # Retourne des zéros si une valeur n'est pas convertible
    
    return defenders, midfielders, forwards, goal_scorers

df_matchs[['home_defenders', 'home_midfielders', 'home_forwards', 'home_goal_scorers']] = (
    df_matchs['formation_home'].apply(extract_positions).apply(pd.Series)
)
df_matchs[['away_defenders', 'away_midfielders', 'away_forwards', 'away_goal_scorers']] = (
    df_matchs['formation_away'].apply(extract_positions).apply(pd.Series)
)


# création d'une colonne comptant le nombre de jours depuis le dernier match de la saison par équipe 
df_matchs = df_matchs.sort_values("date").reset_index(drop=True)

df_matchs["home_victory_serie"] = 0
df_matchs["away_victory_serie"] = 0
df_matchs["home_days_since_last_match"] = 0  # Nouvelle colonne pour le nombre de jours depuis le dernier match (équipe à domicile)
df_matchs["away_days_since_last_match"] = 0  # Nouvelle colonne pour le nombre de jours depuis le dernier match (équipe à l'extérieur)


from collections import defaultdict # On crée une structure pour stocker tous les matchs joués par chaque équipe

match_history = defaultdict(list)

for idx, row in df_matchs.iterrows():
    match_date = row["date"]
    home_team = row["home"]
    away_team = row["away"]
    home_win = row["home_winner"]
    away_win = row["away_winner"]
    
    # Récupère les 5 derniers matchs du club AVANT la date considérée (la date de chaque match)
    def get_last_5_victories(team, current_date):
        history = match_history[team]
        # Ne garder que les matchs avant la date actuelle
        past_matches = [m for m in history if m["date"] < current_date]
        # Trier par date décroissante
        past_matches.sort(key=lambda x: x["date"], reverse=True)
        # Prendre les 5 derniers
        last_5 = past_matches[:5]
        # Compter les victoires
        victories = sum([1 for m in last_5 if m["win"]])
        return victories

    # Calcul de la série de victoires avant ce match
    df_matchs.at[idx, "home_victory_serie"] = get_last_5_victories(home_team, match_date)
    df_matchs.at[idx, "away_victory_serie"] = get_last_5_victories(away_team, match_date)

    # Calcul du nombre de jours depuis le dernier match
    def get_days_since_last_match(team, current_date):
        history = match_history[team]
        # Ne garder que les matchs avant la date actuelle
        past_matches = [m for m in history if m["date"] < current_date]
        if past_matches:
            # Trier par date décroissante et prendre le dernier match
            past_matches.sort(key=lambda x: x["date"], reverse=True)
            last_match_date = past_matches[0]["date"]
            days_since_last_match = (current_date - last_match_date).days
            return days_since_last_match
        else:
            return None  # Aucun match précédent, donc retour de None ou valeur arbitraire

    # Mettre à jour les colonnes "jours depuis le dernier match"
    df_matchs.at[idx, "home_days_since_last_match"] = get_days_since_last_match(home_team, match_date)
    df_matchs.at[idx, "away_days_since_last_match"] = get_days_since_last_match(away_team, match_date)

    # Ensuite on met à jour l’historique de chaque club avec CE match
    match_history[home_team].append({
        "date": match_date,
        "win": home_win
    })
    match_history[away_team].append({
        "date": match_date,
        "win": away_win
    })


df_matchs["year"] = df_matchs["date"].dt.year
df_matchs["month"] = df_matchs["date"].dt.month
df_matchs["day"] = df_matchs["date"].dt.day
df_matchs["dob_coach_home"] = df_matchs["dob_coach_home"].dt.year
df_matchs["dob_coach_away"] = df_matchs["dob_coach_away"].dt.year
df_matchs["clouds"] = df_matchs["clouds"].str.rstrip('%').astype(float) / 100
df_matchs["humidity"] = df_matchs["humidity"].str.rstrip('%').astype(float) / 100

df_final = df_matchs.drop(columns=["match_id", 'league_id', 'state_id', 'venue_id', 'result_info','round', 'home','formation_home','coach_home','away','formation_away', 'coach_away','venue_city','league', 'league_type', 'date'])