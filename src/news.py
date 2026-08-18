import urllib.request
import xml.etree.ElementTree as ET
import re

def _strip_html(text: str) -> str:
    if not text:
        return ""
    clean = re.sub(r'<[^>]+>', '', text)
    clean = re.sub(r'\s+', ' ', clean)
    return clean.strip()

def get_diverse_news():
    feeds = {
        "سیاسی و اجتماعی": "http://feeds.bbci.co.uk/news/world/rss.xml",
        "اقتصادی": "http://feeds.bbci.co.uk/news/business/rss.xml",
        "فرهنگی و هنری": "http://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml",
        "فناوری و علم": "https://hnrss.org/frontpage"
    }
    
    news_data = {}
    for category, url in feeds.items():
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                xml_data = resp.read()
            root = ET.fromstring(xml_data)
            items = []
            for item in root.findall('.//item')[:2]:
                title = item.find('title').text if item.find('title') is not None else ''
                link = item.find('link').text if item.find('link') is not None else ''
                desc = item.find('description').text if item.find('description') is not None else ''
                
                items.append({
                    "title": _strip_html(title),
                    "summary": _strip_html(desc),
                    "link": link.strip()
                })
            news_data[category] = items
        except Exception:
            continue
            
    return news_data
