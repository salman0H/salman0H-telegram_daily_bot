import json
import urllib.request
from src import config

def get_sports_results():
    results = {"Soccer": [], "Basketball": [], "Volleyball": []}
    headers = {"User-Agent": "Mozilla/5.0"}
    
    if config.SPORTRADAR_SOCCER_API_KEY:
        url = f"https://api.sportradar.com/soccer/trial/v4/en/schedules/live/summaries.json?api_key={config.SPORTRADAR_SOCCER_API_KEY}"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                for s in data.get("summaries", [])[:3]:
                    competitors = s.get("sport_event", {}).get("competitors", [])
                    if len(competitors) == 2:
                        results["Soccer"].append(f"{competitors[0]['name']} ⚽ {competitors[1]['name']}")
        except Exception as e:
            print(f"Soccer Fetch Error: {e}")

    if config.SPORTRADAR_BASKETBALL_API_KEY:
        url = f"https://api.sportradar.com/basketball/trial/v2/en/schedules/live/summaries.json?api_key={config.SPORTRADAR_BASKETBALL_API_KEY}"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                for s in data.get("summaries", [])[:3]:
                    competitors = s.get("sport_event", {}).get("competitors", [])
                    if len(competitors) == 2:
                        results["Basketball"].append(f"{competitors[0]['name']} 🏀 {competitors[1]['name']}")
        except Exception as e:
            print(f"Basketball Fetch Error: {e}")

    return results