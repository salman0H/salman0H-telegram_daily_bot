import json
import re
import random
import urllib.request
import urllib.error
from src import config

def _clean_output(text: str) -> str:
    if not text:
        return text
        
    text = re.sub(r'[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]+', '', text)
    text = text.replace('\xa0', ' ').replace('\u200b', '')
    text = re.sub(r'^\s*#+\s*', '', text, flags=re.MULTILINE)
    text = text.replace('##', '').replace('#', '')
    text = re.sub(r'\n\s*\n(http)', r'\n\n\1', text)

    open_b_count = text.count('<b>')
    close_b_count = text.count('</b>')
    if open_b_count > close_b_count:
        text = text.rstrip() + '</b>' * (open_b_count - close_b_count)

    return text.strip()

def _call_groq(prompt: str, temperature: float = 0.2, fallback_data: str = None) -> str:
    for model in config.GROQ_MODELS:
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system", 
                    "content": (
                        "You are a strict Persian news and knowledge editor. "
                        "MANDATORY RULES:\n"
                        "1. Output exclusively in pure Persian.\n"
                        "2. NEVER mix English and Persian letters in a single word.\n"
                        "3. NEVER use HTML tags like <i> or <blockquote>. ONLY <b> is allowed for titles.\n"
                        "4. NEVER use Markdown headings like # or ##."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": 600
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
                choice = result["choices"][0]
                finish_reason = choice.get("finish_reason", "unknown")
                raw_text = choice.get("message", {}).get("content", "")
                
                print(f"[Groq API] Model: {model}, finish_reason: {finish_reason}")
                if finish_reason == "length":
                    print("[Groq Warning] Response was truncated! Increase max_tokens.")
                    
                return _clean_output(raw_text)
        except urllib.error.HTTPError as e:
            err_str = e.read().decode('utf-8')
            print(f"[Groq API Error] Model '{model}' failed: {err_str}")
            continue
        except Exception as e:
            print(f"[Network Error] {e}")
            continue

    print("Critical: All Groq models failed. Executing zero-data-loss fallback.")
    if fallback_data:
        return fallback_data
    raise RuntimeError("Groq API Exhausted and no fallback data provided.")

def elaborate_news(news_data: dict) -> str:
    if not news_data:
        return "خبر جدیدی یافت نشد."

    raw_fallback = ""
    for category, items in news_data.items():
        raw_fallback += f"<b>{category}</b>\n"
        for item in items:
            raw_fallback += f"🔹 <b>{item.get('title', '')}</b>\n{item.get('summary', '')}\n{item.get('link', '')}\n\n"

    prompt = (
        "Format the news into Persian updates.\n"
        "CRITICAL RULES:\n"
        "1. Write the category title using <b>Category Name</b>.\n"
        "2. Start each news item with a BOLD title: <b>Title Here</b>.\n"
        "3. Follow with a 2-3 sentence description and 2 bullet points (🔹).\n"
        "4. Place the exact URL on a new line at the end.\n"
        "5. DO NOT use HTML tags (no <blockquote>, no <i>). Use ONLY <b> for bold.\n\n"
        f"Data: {json.dumps(news_data)}"
    )
    return _call_groq(prompt, temperature=0.2, fallback_data=raw_fallback.strip())

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
    
    fallback_insight = "سرویس پردازش زبان طبیعی در حال حاضر با افت ترافیک مواجه است. فردا با دانش روز جدید بازخواهیم گشت."

    prompt = (
        "Generate 4 distinct 'Daily Insights' in pure Persian based on these topics:\n"
        f"1. {selected_topics[0]}\n"
        f"2. {selected_topics[1]}\n"
        f"3. {selected_topics[2]}\n"
        f"4. {selected_topics[3]}\n\n"
        "STRICT FORMAT RULES:\n"
        "- Format each topic's title exactly like this: 🔹 <b>[Topic Name]</b>\n"
        "- Write a highly informative, expert-level paragraph (3-4 sentences) directly below the title.\n"
        "- For coding topics, include code snippets using standard markdown: ```language ... ```\n"
        "- ABSOLUTELY NO HTML TAGS except <b>.\n"
        "- Separate each topic section with a double blank line (\\n\\n)."
    )
    return _call_groq(prompt, temperature=0.3, fallback_data=fallback_insight)
