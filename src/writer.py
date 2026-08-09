import json
import urllib.request
import urllib.error
from src import config

def _call_groq(prompt: str, temperature: float = 0.3) -> str:
    payload = {
        "model": config.GROQ_MODEL,
        "messages": [
            {
                "role": "system", 
                "content": "You are a professional Persian tech and news editor. You MUST output exclusively in fluent Persian. NO Chinese, NO Cyrillic, NO translation artifacts. Maintain absolute formatting compliance."
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
            return result["choices"][0]["message"]["content"].strip()
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Groq API Error: {e.read().decode('utf-8')}")

def elaborate_news(news_data: dict) -> str:
    if not news_data:
        return "خبر جدیدی یافت نشد."

    prompt = (
        "Format the provided news data into professional Persian updates.\n"
        "RULES:\n"
        "1. Write the category name wrapped in <b> tags.\n"
        "2. For each news item, create a descriptive Persian paragraph (3-4 sentences) based on the title and summary. Expand on the facts logically. DO NOT duplicate the title.\n"
        "3. Use bullet points (🔹) for key details if applicable.\n"
        "4. Insert EXACTLY ONE blank line before the URL.\n"
        "5. Wrap each complete news item (text and URL) inside <blockquote> tags.\n\n"
        f"Data: {json.dumps(news_data)}"
    )
    return _call_groq(prompt, temperature=0.3)

def generate_daily_insight() -> str:
    prompt = (
        "Generate 4 distinct 'Daily Insights' in pure, high-quality Persian:\n"
        "1. Software/IT Architecture (Include a practical code snippet or CLI command).\n"
        "2. Philosophy (A profound thought or principle).\n"
        "3. Book Extract (A detailed key takeaway from a notable non-fiction book).\n"
        "4. Historical Fact (A fascinating event in computing or world history).\n\n"
        "CRITICAL FORMATTING:\n"
        "- Category titles MUST be wrapped in <b> tags.\n"
        "- Write detailed, insightful paragraphs (3-4 sentences per category).\n"
        "- Wrap the Philosophy, Book, and History content inside <blockquote> tags.\n"
        "- Format code with standard markdown: ```language ... ```\n"
        "- ABSOLUTELY NO CHINESE CHARACTERS."
    )
    return _call_groq(prompt, temperature=0.4)