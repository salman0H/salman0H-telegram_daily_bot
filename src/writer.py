import json
import re
import random
import urllib.request
import urllib.error
from src import config

def _clean_output(text: str) -> str:
    text = re.sub(r'[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]+', '', text)
    text = text.replace('\xa0', ' ').replace('\u200b', '')
    text = re.sub(r'^\s*#+\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n\s*\n(http)', r'\n\n\1', text)
    return text.strip()

def _call_groq(prompt: str, temperature: float = 0.2) -> str:
    payload = {
        "model": config.GROQ_MODEL,
        "messages": [
            {
                "role": "system", 
                "content": (
                    "You are a strict Persian news and knowledge editor. "
                    "MANDATORY RULES:\n"
                    "1. Output exclusively in pure Persian.\n"
                    "2. NEVER use markdown headings like # or ##.\n"
                    "3. Maintain exact Telegram HTML compliance."
                )
            },
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature
    }
    headers = {
        "Authorization": f"Bearer {config.GROQ_API_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(config.GROQ_API_URL, data=data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            raw_text = result["choices"][0]["message"]["content"]
            return _clean_output(raw_text)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Groq API Error: {e.read().decode('utf-8')}")

def elaborate_news(news_data: dict) -> str:
    if not news_data:
        return "خبر جدیدی یافت نشد."

    prompt = (
        "Format the news into Persian updates.\n"
        "CRITICAL RULES:\n"
        "1. Write the category title using <b>Category</b>.\n"
        "2. EVERY news item MUST be placed inside a <blockquote> tag.\n"
        "3. Inside the <blockquote>, start with a BOLD title for that specific news: <b>Title Here</b>.\n"
        "4. Follow with a 2-3 sentence description and 2 bullet points (🔹).\n"
        "5. Place the exact URL on a new line at the end of the blockquote.\n"
        "6. DO NOT USE MARKDOWN HEADINGS (# or ##).\n\n"
        f"Data: {json.dumps(news_data)}"
    )
    return _call_groq(prompt, temperature=0.2)

def generate_daily_insight() -> str:
    topics_pool = [
        "معماری نرم‌افزار و مهندسی سیستم‌ها",
        "نکات کاربردی لینوکس، داکر یا گیت",
        "معرفی و خلاصه یک کتاب برجسته غیرداستانی",
        "یک فکت شگفت‌انگیز تاریخی",
        "مبانی و مفاهیم پیشرفته زبان‌های برنامه‌نویسی",
        "طراحی الگوریتم‌ها و ساختمان داده (CLRS)",
        "شبکه‌های عصبی پیش‌خور و پردازش زبان طبیعی (NLP)",
        "اصول رباتیک، کینماتیک و کنترل",
        "جریان‌شناسی سیاسی و تاریخ انقلاب اسلامی",
        "تاریخ، تبارشناسی و شناسنامه انبیا و ائمه اطهار",
        "تحلیل بیومکانیک و آناتومی فنون ضربه‌ای کاراته",
        "جهان اساطیر: خدایان، قهرمانان و هیولاهای باستان",
        "سیر تحول اندیشه در فلسفه اسلامی و غربی"
    ]
    
    selected_topics = random.sample(topics_pool, 4)
    
    prompt = (
        "Generate 4 distinct 'Daily Insights' in pure Persian based on these topics:\n"
        f"1. {selected_topics[0]}\n"
        f"2. {selected_topics[1]}\n"
        f"3. {selected_topics[2]}\n"
        f"4. {selected_topics[3]}\n\n"
        "STRICT FORMAT:\n"
        "- Category title MUST be formatted ONLY as <b>Title</b> (NO # OR ## Markdown headings!).\n"
        "- The insight content MUST be inside a <blockquote> tag.\n"
        "- For coding topics, include code snippets using ```language ... ``` markdown."
    )
    return _call_groq(prompt, temperature=0.3)
