import sys
from src import weather, news, sports, song, writer, telegram_sender

def run():
    weather_data = weather.get_mashhad_weather()
    if weather_data:
        w_msg = (
            "🌤 <b>وضعیت آب‌وهوا</b>\n\n"
            f"دما: {weather_data.get('temp')}°C\n"
            f"رطوبت: {weather_data.get('humidity')}٪\n"
            f"باد: {weather_data.get('wind_speed')} m/s\n"
            f"آسمان: {weather_data.get('description')}"
        )
        telegram_sender.send_message(w_msg)

    try:
        insight = writer.generate_daily_insight()
        telegram_sender.send_message(f"💡 <b>دانش روز</b>\n\n{insight}")
    except Exception as e:
        print(f"Insight Error: {e}")

    news_items = news.get_diverse_news()
    if news_items:
        news_text = writer.elaborate_news(news_items)
        telegram_sender.send_message(f"📰 <b>اخبار امروز</b>\n\n{news_text}")

    sports_data = sports.get_sports_results()
    if any(sports_data.values()):
        s_msg = "🏆 <b>نتایج زنده ورزشی</b>\n\n"
        for sport, matches in sports_data.items():
            if matches:
                s_msg += f"▪️ <b>{sport}</b>\n"
                for m in matches:
                    s_msg += f"<blockquote>{m}</blockquote>\n"
                s_msg += "\n"
        telegram_sender.send_message(s_msg.strip())

    target_song = song.get_trending_song()
    audio_file = song.download_audio(target_song) if target_song else None
    
    if audio_file:
        telegram_sender.send_audio(audio_file, caption=f"🎵 <b>آهنگ روز</b>\n\n{target_song}")
    else:
        apple_top_5 = song.get_apple_music_top_5()
        telegram_sender.send_message(apple_top_5)

if __name__ == "__main__":
    run()