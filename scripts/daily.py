"""Conservative daily publisher: official release feeds only, fail closed."""
import hashlib
import json
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse

import feedparser
import requests
import yaml
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
POSTS = ROOT / 'src/content/posts'
FEEDS = [
    ('Google Gemini CLI', 'https://github.com/google-gemini/gemini-cli/releases.atom', 'github.com'),
    ('Microsoft MarkItDown', 'https://github.com/microsoft/markitdown/releases.atom', 'github.com'),
    ('Ollama', 'https://github.com/ollama/ollama/releases.atom', 'github.com'),
]
SESSION = requests.Session()
SESSION.headers['User-Agent'] = 'RadarIALatam/1.0 (+public editorial feed reader)'


def canonical(url):
    p = urlparse(url)
    if p.scheme != 'https' or p.hostname != 'github.com' or p.username or p.password:
        raise ValueError('URL fuera de fuente permitida')
    return f'https://{p.hostname}{p.path.rstrip("/")}'


def published(entry):
    t = entry.get('published_parsed') or entry.get('updated_parsed')
    if not t:
        raise ValueError('Sin fecha de fuente')
    return datetime(*t[:6], tzinfo=timezone.utc)


def gemini(source):
    key = os.environ['GEMINI_API_KEY']
    model = os.environ.get('GEMINI_MODEL', 'gemini-2.5-flash-lite')
    prompt = '''Eres editor de tecnología para Colombia/Latinoamérica. Devuelve SOLO JSON con title, description, body y claims (lista de frases factuales del texto). Escribe en español claro. Usa únicamente los datos de la fuente; no infieras precios, disponibilidad regional, promociones ni gratuidad. Explica para quién sirve, un ejemplo práctico y una limitación. Si es solo un parche menor o no hay suficiente información útil, devuelve {"skip":true}. Body en Markdown, 140-300 palabras, sin HTML, sin títulos H1 y con enlace a la fuente. Fuente:\n''' + json.dumps(source, ensure_ascii=False)
    url = f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent'
    r = SESSION.post(url, params={'key': key}, json={'contents': [{'parts': [{'text': prompt}]}], 'generationConfig': {'responseMimeType': 'application/json', 'temperature': 0.2}}, timeout=45)
    r.raise_for_status()
    return json.loads(r.json()['candidates'][0]['content']['parts'][0]['text'])


def quality(draft, source):
    if draft.get('skip'):
        return False
    title, desc, body = (draft.get(k, '') for k in ('title', 'description', 'body'))
    if not 25 <= len(title) <= 90 or not 70 <= len(desc) <= 170 or not 140 <= len(body.split()) <= 300:
        return False
    if not source['url'] in body or any(x in body.lower() for x in ['oferta por tiempo limitado', 'gratis para todos', 'descuento exclusivo']):
        return False
    if re.search(r'<[^>]+>|https?://(?!github\.com)', body):
        return False
    claims = draft.get('claims')
    if not isinstance(claims, list) or not 1 <= len(claims) <= 8:
        return False
    # Independent factual review by the model; any uncertainty rejects publication.
    review = gemini_review(source, draft)
    return review.get('supported') is True and review.get('useful') is True and review.get('regional_claims') is False


def gemini_review(source, draft):
    key = os.environ['GEMINI_API_KEY']
    model = os.environ.get('GEMINI_MODEL', 'gemini-2.5-flash-lite')
    prompt = 'Evalúa estrictamente el borrador frente a la fuente. Responde SOLO JSON: supported (bool), useful (bool), regional_claims (bool). supported=false si cualquier afirmación sobre características, precio o fechas no está explícitamente sustentada. regional_claims=true si afirma acceso o precio específico para Colombia/Latam sin evidencia.\n' + json.dumps({'source': source, 'draft': draft}, ensure_ascii=False)
    r = SESSION.post(f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent', params={'key': key}, json={'contents': [{'parts': [{'text': prompt}]}], 'generationConfig': {'responseMimeType': 'application/json', 'temperature': 0}}, timeout=45)
    r.raise_for_status()
    return json.loads(r.json()['candidates'][0]['content']['parts'][0]['text'])


def main():
    if not os.environ.get('GEMINI_API_KEY'):
        print('Sin GEMINI_API_KEY: se omite publicación.')
        return
    now = datetime.now(timezone.utc)
    existing = set()
    for post in POSTS.glob('*.md'):
        raw = post.read_text(encoding='utf-8')
        match = re.match(r'\A---\n(.*?)\n---', raw, re.S)
        if match:
            existing.add(yaml.safe_load(match.group(1)).get('sourceUrl'))
    for name, feed_url, _ in FEEDS:
        try:
            resp = SESSION.get(feed_url, timeout=20)
            resp.raise_for_status()
            feed = feedparser.parse(resp.content)
            if feed.bozo:
                raise ValueError('Feed inválido')
            for entry in feed.entries[:5]:
                url = canonical(entry.link)
                repo_path = urlparse(feed_url).path.removesuffix('/releases.atom')
                if not urlparse(url).path.startswith(repo_path + '/releases/'):
                    continue
                date = published(entry)
                if url in existing or not now - timedelta(days=7) <= date <= now + timedelta(hours=2):
                    continue
                page = SESSION.get(url, timeout=20, allow_redirects=False)
                page.raise_for_status()
                if len(page.content) > 1_000_000:
                    continue
                text = BeautifulSoup(page.text, 'html.parser').get_text(' ', strip=True)
                summary = BeautifulSoup(entry.get('summary', ''), 'html.parser').get_text(' ', strip=True)
                if len(summary) < 120 or not entry.title or not text or entry.title.lower() not in text.lower():
                    continue
                source = {'publisher': name, 'title': entry.title, 'date': date.isoformat(), 'url': url, 'official_excerpt': summary[:4000]}
                draft = gemini(source)
                if not quality(draft, source):
                    print('Rechazado por calidad:', url)
                    continue
                slug = re.sub(r'[^a-z0-9-]+', '-', entry.title.lower()).strip('-')[:55] + '-' + hashlib.sha256(url.encode()).hexdigest()[:8]
                front = {'title': draft['title'], 'description': draft['description'], 'pubDate': now.date().isoformat(), 'sourceUrl': url, 'sourceDate': date.date().isoformat(), 'kind': 'novedad', 'verifiedAt': now.isoformat(), 'tags': ['novedades', name]}
                content = '---\n' + yaml.safe_dump(front, allow_unicode=True, sort_keys=False) + '---\n\n' + draft['body'].strip() + '\n'
                (POSTS / f'{slug}.md').write_text(content, encoding='utf-8')
                print('Publicado:', slug)
                return  # one useful article per day maximum
        except (requests.RequestException, ValueError, KeyError, IndexError, json.JSONDecodeError) as exc:
            print(f'Fuente omitida {name}: {exc}')
    print('Sin novedades publicables hoy.')


if __name__ == '__main__':
    main()
