import json
import urllib.request
from datetime import datetime
from src import config

def get_mashhad_weather():
    current_url = f"https://api.openweathermap.org/data/2.5/weather?lat={config.MASHHAD_LAT}&lon={config.MASHHAD_LON}&units=metric&appid={config.OPENWEATHER_API_KEY}"
    forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={config.MASHHAD_LAT}&lon={config.MASHHAD_LON}&units=metric&appid={config.OPENWEATHER_API_KEY}"
    
    weather_info = {
        "current": {"temp": "N/A", "humidity": "N/A", "description": "N/A", "wind_speed": "N/A"},
        "forecast": []
    }
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        req_c = urllib.request.Request(current_url, headers=headers)
        with urllib.request.urlopen(req_c, timeout=10) as resp:
            data_c = json.loads(resp.read().decode("utf-8"))
            weather_info["current"] = {
                "temp": data_c["main"]["temp"],
                "humidity": data_c["main"]["humidity"],
                "description": data_c["weather"][0]["description"],
                "wind_speed": data_c["wind"]["speed"]
            }

        req_f = urllib.request.Request(forecast_url, headers=headers)
        with urllib.request.urlopen(req_f, timeout=10) as resp:
            data_f = json.loads(resp.read().decode("utf-8"))
            today_date = datetime.utcnow().strftime("%Y-%m-%d")
            
            for item in data_f.get("list", []):
                dt_txt = item.get("dt_txt", "")
                if dt_txt.startswith(today_date):
                    time_str = dt_txt.split(" ")[1][:5]
                    temp = item["main"]["temp"]
                    desc = item["weather"][0]["description"]
                    weather_info["forecast"].append(f"ساعت {time_str}: {temp}°C | {desc}")
                    
    except Exception:
        pass
        
    return weather_info
