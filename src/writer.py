import json
import re
import random
import urllib.request
import urllib.error
from src import config

def _clean_output(text: str) -> str:
    # Remove CJK characters (Chinese, Japanese, Korean) completely
    text = re.sub(r'[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]+', '', text)
    # Remove zero-width spaces and non-breaking spaces
    text = text.replace('\xa0', ' ').replace('\u200b', '')
    # Enforce exactly one blank line before URLs
    text = re.sub(r'\n\s*\n(http)', r'\n\n\1', text)
    return text.strip()

def _call_groq(prompt: str, temperature: float = 0.2) -> str:
    payload = {
        "model": config.GROQ_MODEL,
        "messages": [
            {
                "role": "system", 
                "content": (
                    "You are a strict, highly specialized Persian academic and news editor. "
                    "MANDATORY RULES:\n"
                    "1. Output exclusively in pure, native Persian. No conversational fillers.\n"
                    "2. Translate all foreign words into Persian UNLESS they are globally recognized technical terms.\n"
                    "3. Absolutely NO Chinese, Japanese, or Cyrillic characters under any circumstance.\n"
                    "4. Maintain exact formatting compliance."
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
        "Format the provided news data into professional Persian updates.\n"
        "RULES:\n"
        "1. Write the category name wrapped in <b> tags.\n"
        "2. For each news item, create a descriptive Persian paragraph (3-4 sentences). Expand on facts logically without duplicating the title.\n"
        "3. Use bullet points (🔹) for key details.\n"
        "4. Insert EXACTLY ONE blank line before the URL.\n"
        "5. Wrap each complete news item (text and URL) inside <blockquote> tags.\n\n"
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
        "Generate 4 distinct 'Daily Insights' in pure, high-quality Persian based EXACTLY on these 4 randomly selected topics:\n"
        f"1. {selected_topics[0]}\n"
        f"2. {selected_topics[1]}\n"
        f"3. {selected_topics[2]}\n"
        f"4. {selected_topics[3]}\n\n"
        "CRITICAL FORMATTING:\n"
        "- Category titles MUST be wrapped in <b> tags (e.g., <b>فلسفه اسلامی</b>).\n"
        "- Write a highly informative, expert-level paragraph (3-4 sentences) for each topic.\n"
        "- Wrap the content paragraph inside <blockquote> tags.\n"
        "- If a topic is related to programming/IT/algorithms, include a very short code snippet or command using standard markdown: ```language ... ```\n"
        "- NO conversational intro or outro. Output only the requested blocks."
    )
    return _call_groq(prompt, temperature=0.4)