import json
import urllib.request
from datetime import datetime, timedelta
from src import config

def get_sports_results():
    results = {"Soccer": [], "Basketball": []}
    headers = {"User-Agent": "Mozilla/5.0"}
    
    yesterday = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    if config.SPORTRADAR_SOCCER_API_KEY:
        url = f"https://api.sportradar.com/soccer/trial/v4/en/schedules/{yesterday}/summaries.json?api_key={config.SPORTRADAR_SOCCER_API_KEY}"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                for s in data.get("summaries", [])[:5]:
                    event = s.get("sport_event", {})
                    status = s.get("sport_event_status", {})
                    competitors = event.get("competitors", [])
                    
                    if len(competitors) == 2:
                        home = competitors[0].get("name", "Home")
                        away = competitors[1].get("name", "Away")
                        h_score = status.get("home_score", "?")
                        a_score = status.get("away_score", "?")
                        
                        results["Soccer"].append(f"{home} {h_score} - {a_score} {away}")
        except Exception:
            pass

    if config.SPORTRADAR_BASKETBALL_API_KEY:
        url = f"https://api.sportradar.com/basketball/trial/v2/en/schedules/{yesterday}/summaries.json?api_key={config.SPORTRADAR_BASKETBALL_API_KEY}"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                for s in data.get("summaries", [])[:5]:
                    event = s.get("sport_event", {})
                    status = s.get("sport_event_status", {})
                    competitors = event.get("competitors", [])
                    
                    if len(competitors) == 2:
                        home = competitors[0].get("name", "Home")
                        away = competitors[1].get("name", "Away")
                        h_score = status.get("home_score", "?")
                        a_score = status.get("away_score", "?")
                        
                        results["Basketball"].append(f"{home} {h_score} - {a_score} {away}")
        except Exception:
            pass

    return results
