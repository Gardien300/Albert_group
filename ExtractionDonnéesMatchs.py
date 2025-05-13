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



