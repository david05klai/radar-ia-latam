"""Optional single post to a Telegram channel controlled by the site owner."""
import os
import re
import subprocess
from pathlib import Path
import requests
import yaml

token = os.getenv('TELEGRAM_BOT_TOKEN')
chat = os.getenv('TELEGRAM_CHAT_ID')
site = os.getenv('SITE_URL', '').rstrip('/')
if not all((token, chat, site)):
    print('Difusión omitida: canal no configurado.')
    raise SystemExit(0)
path = subprocess.check_output(['git', 'diff-tree', '--no-commit-id', '--name-only', '-r', 'HEAD'], text=True).strip().splitlines()
posts = [Path(p) for p in path if p.startswith('src/content/posts/') and p.endswith('.md')]
if len(posts) != 1:
    raise SystemExit(0)
raw = posts[0].read_text(encoding='utf-8')
data = yaml.safe_load(re.match(r'\A---\n(.*?)\n---', raw, re.S).group(1))
message = f"{data['title']}\n\n{data['description']}\n\n{site}/blog/{posts[0].stem}/?utm_source=telegram&utm_medium=social&utm_campaign=novedades"
response = requests.post(f'https://api.telegram.org/bot{token}/sendMessage', json={'chat_id': chat, 'text': message, 'disable_web_page_preview': False}, timeout=15)
response.raise_for_status()
print('Difusión enviada.')
