import sys
import json
import uuid
import os
import re
import html
import mimetypes
import urllib.request
import urllib.error
from src import config

def _resolve_target():
    chan_id = str(config.TELEGRAM_CHANNEL_ID).strip()
    user_id = str(config.TELEGRAM_USER_ID).strip()

    if chan_id and chan_id.lower() not in ["null", "none", ""]:
        return chan_id
    if user_id and user_id.lower() not in ["null", "none", ""]:
        return user_id
        
    sys.exit("Critical: Valid TELEGRAM_CHANNEL_ID or TELEGRAM_USER_ID not found.")

def _sanitize_for_telegram_html(text: str) -> str:
    if not text:
        return ""

    if text.count('```') % 2 != 0:
        text += '\n```\n'
        
    text = text.replace('<blockquote>', '').replace('</blockquote>', '')
    text = text.replace('<b>', '**').replace('</b>', '**')
    
    text = html.escape(text, quote=False)
    text = re.sub(r'^\s*#+\s*', '', text, flags=re.MULTILINE)
    
    text = re.sub(r'```(\w+)?\s*\n(.*?)\s*```', r'<pre><code class="language-\1">\2</code></pre>', text, flags=re.DOTALL)
    text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    
    open_b = text.count('<b>')
    close_b = text.count('</b>')
    if open_b > close_b:
        text += '</b>' * (open_b - close_b)
        
    return text.strip()

def send_message(text: str):
    chat_id = _resolve_target()
    text = _sanitize_for_telegram_html(text)
    
    if len(text) > 4096:
        text = text[:4090] + "..."

    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": True,
        "parse_mode": "HTML"
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        payload.pop("parse_mode", None)
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=15) as retry_resp:
                return json.loads(retry_resp.read().decode("utf-8"))
        except urllib.error.HTTPError as retry_e:
            sys.exit(f"Telegram API Error ({retry_e.code}): {retry_e.read().decode('utf-8')}")

def send_audio(file_path: str, caption: str = ""):
    if not file_path or not os.path.exists(file_path):
        return None

    chat_id = _resolve_target()
    caption = _sanitize_for_telegram_html(caption)
    boundary = uuid.uuid4().hex
    headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"}
    body = bytearray()

    fields = {"chat_id": chat_id, "caption": caption, "parse_mode": "HTML"}
    for k, v in fields.items():
        body.extend(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode("utf-8"))

    filename = os.path.basename(file_path)
    mime_type = mimetypes.guess_type(filename)[0] or "audio/mpeg"
    body.extend(f"--{boundary}\r\nContent-Disposition: form-data; name=\"audio\"; filename=\"{filename}\"\r\nContent-Type: {mime_type}\r\n\r\n".encode("utf-8"))
    
    with open(file_path, "rb") as f:
        body.extend(f.read())
    body.extend(f"\r\n--{boundary}--\r\n".encode("utf-8"))

    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendAudio"
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError:
        return None
