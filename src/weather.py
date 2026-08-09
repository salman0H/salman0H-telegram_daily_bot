import json
import urllib.request
import urllib.error
from src import config

def get_mashhad_weather():
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={config.MASHHAD_LAT}&lon={config.MASHHAD_LON}&units=metric&appid={config.OPENWEATHER_API_KEY}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return {
                "temp": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "description": data["weather"][0]["description"],
                "wind_speed": data["wind"]["speed"]
            }
    except Exception as e:
        print(f"Weather Fetch Error: {e}")
        return {"temp": "N/A", "humidity": "N/A", "description": "N/A", "wind_speed": "N/A"}