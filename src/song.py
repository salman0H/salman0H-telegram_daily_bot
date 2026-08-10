import json
import base64
import urllib.request
import urllib.parse
import subprocess
from src import config

def get_trending_song():
    if not config.SPOTIFY_CLIENT_ID or not config.SPOTIFY_CLIENT_SECRET:
        return None

    auth_str = f"{config.SPOTIFY_CLIENT_ID}:{config.SPOTIFY_CLIENT_SECRET}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()
    
    token_url = "https://accounts.spotify.com/api/token"
    token_data = urllib.parse.urlencode({'grant_type': 'client_credentials'}).encode('utf-8')
    token_headers = {
        "Authorization": f"Basic {b64_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    try:
        req = urllib.request.Request(token_url, data=token_data, headers=token_headers, method="POST")
        with urllib.request.urlopen(req) as resp:
            token_res = json.loads(resp.read().decode("utf-8"))
        
        playlist_url = "https://api.spotify.com/v1/browse/new-releases?limit=1"
        auth_header = {"Authorization": f"Bearer {token_res['access_token']}"}
        req_play = urllib.request.Request(playlist_url, headers=auth_header)
        
        with urllib.request.urlopen(req_play) as resp_play:
            track_res = json.loads(resp_play.read().decode("utf-8"))
            
        item = track_res["albums"]["items"][0]
        return f"{item['artists'][0]['name']} - {item['name']}"
    except Exception as e:
        print(f"Spotify Fetch Error: {e}")
        return None

def download_audio(query):
    if not query:
        return None
        
    output_tmpl = "downloaded_song.%(ext)s"
    search_query = f"ytsearch1:{query} audio"
    
    command = [
        "yt-dlp",
        "--extract-audio",
        "--audio-format", "mp3",
        "--max-filesize", "45M",
        "--force-ipv4",
        "--geo-bypass",
        "--sleep-requests", "2",
        "-o", output_tmpl,
        search_query
    ]
    
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"yt-dlp error: {result.stderr}")
        return None
    return "downloaded_song.mp3"

def get_apple_music_top_5():
    url = "https://itunes.apple.com/us/rss/topsongs/limit=5/json"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            entries = data.get("feed", {}).get("entry", [])
            if not entries:
                return "اطلاعات چارت اپل موزیک در دسترس نیست."
            
            result_text = "🎧 <b>۵ آهنگ برتر امروز Apple Music:</b>\n\n"
            for idx, entry in enumerate(entries, 1):
                title = entry.get("im:name", {}).get("label", "Unknown")
                artist = entry.get("im:artist", {}).get("label", "Unknown")
                result_text += f"{idx}. {artist} - {title}\n"
            return result_text.strip()
    except Exception as e:
        print(f"Apple Music Fetch Error: {e}")
        return "خطا در دریافت لیست آهنگ‌های برتر."