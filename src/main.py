import sys
from src import weather, news, sports, song, writer, telegram_sender

def run():
    weather_data = weather.get_mashhad_weather()
    if weather_data and weather_data["current"]["temp"] != "N/A":
        current = weather_data["current"]
        w_msg = (
            "🌤 **وضعیت آب‌وهوا**\n\n"
            f"دما: {current.get('temp')}°C\n"
            f"رطوبت: {current.get('humidity')}٪\n"
            f"باد: {current.get('wind_speed')} m/s\n"
            f"آسمان: {current.get('description')}\n\n"
            "⏱ **پیش‌بینی ساعات آینده:**\n"
        )
        
        if weather_data["forecast"]:
            for f in weather_data["forecast"]:
                w_msg += f"▪️ {f}\n"
        else:
            w_msg += "داده‌های ساعات آینده در دسترس نیست.\n"
            
        telegram_sender.send_message(w_msg.strip())

    try:
        insight = writer.generate_daily_insight()
        telegram_sender.send_message(f"💡 **دانش روز**\n\n{insight}")
    except Exception:
        pass

    news_items = news.get_diverse_news()
    if news_items:
        news_text = writer.elaborate_news(news_items)
        telegram_sender.send_message(f"📰 **اخبار امروز**\n\n{news_text}")

    sports_data = sports.get_sports_results()
    if any(sports_data.values()):
        s_msg = "🏆 **نتایج مسابقات دیروز**\n\n"
        for sport, matches in sports_data.items():
            if matches:
                s_msg += f"▪️ **{sport}**\n\n"
                for m in matches:
                    s_msg += f"⚽ {m}\n"
                s_msg += "\n"
        telegram_sender.send_message(s_msg.strip())

    target_song = song.get_trending_song()
    audio_file = song.download_audio(target_song) if target_song else None
    
    if audio_file:
        telegram_sender.send_audio(audio_file, caption=f"🎵 **آهنگ روز**\n\n{target_song}")
    else:
        apple_top_5 = song.get_apple_music_top_5()
        telegram_sender.send_message(apple_top_5)

if __name__ == "__main__":
    run()
