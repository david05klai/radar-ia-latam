from pathlib import Path
from urllib.parse import urlparse
import re
import yaml

posts = list((Path(__file__).resolve().parents[1] / 'src/content/posts').glob('*.md'))
assert posts, 'Falta contenido'
urls = set()
for post in posts:
    text = post.read_text(encoding='utf-8')
    match = re.match(r'\A---\n(.*?)\n---\n(.*)', text, re.S)
    assert match, f'Frontmatter inválido: {post}'
    data = yaml.safe_load(match[1])
    for key in ('title', 'description', 'pubDate', 'sourceUrl', 'sourceDate', 'kind', 'verifiedAt', 'tags'):
        assert data.get(key), f'{post}: falta {key}'
    assert urlparse(data['sourceUrl']).scheme == 'https'
    assert data['sourceUrl'] not in urls, f'Duplicado: {post}'
    urls.add(data['sourceUrl'])
    assert len(match[2].split()) >= 100, f'{post}: contenido muy corto'
print(f'{len(posts)} publicaciones válidas')
