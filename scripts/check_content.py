"""Check English-only source, local HTML links/anchors and API metadata hygiene."""
import argparse
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]

class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.links = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        if tag == 'a' and attrs.get('name'):
            self.ids.add(attrs['name'])
        for attribute in ('href', 'src'):
            if attrs.get(attribute):
                self.links.append(attrs[attribute])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--site', type=Path, required=True)
    args = parser.parse_args()
    site = args.site.resolve()
    problems = []
    for path in (ROOT / 'docs/en').rglob('*.md'):
        source = path.read_text(encoding='utf-8')
        # The Korean language's name is a valid sample UI label; prose must be English.
        if re.search(r'[\uac00-\ud7a3]', source.replace('한국어', '')):
            problems.append(f'Non-English prose: {path.relative_to(ROOT)}')
        if re.search(r'(?:(?<![A-Za-z])[A-Za-z]:[\\/]|file:///|\.work/|\.work\\)', source):
            problems.append(f'Local machine path in guide: {path.relative_to(ROOT)}')
    for path in (ROOT / 'api-metadata').rglob('*.yml'):
        source = path.read_text(encoding='utf-8')
        if re.search(r'(?:(?<![A-Za-z])[A-Za-z]:[\\/]|file:///|D%3A|C%3A)', source):
            problems.append(f'Local machine path in API metadata: {path.name}')
    pages = {}
    for path in site.rglob('*.html'):
        page = Page()
        page.feed(path.read_text(encoding='utf-8'))
        pages[path.resolve()] = page
    for path, page in pages.items():
        for link in page.links:
            url = urlsplit(link)
            if url.scheme or url.netloc or link.startswith('data:'):
                continue
            if not url.path:
                target = path
            else:
                decoded = unquote(url.path)
                # GitHub Pages canonical root includes the repository slug.
                decoded = decoded.removeprefix('/2d-tower-defense-maker/') if decoded.startswith('/') else decoded
                target = ((site / decoded) if url.path.startswith('/') else (path.parent / decoded)).resolve()
                if target.is_dir():
                    target /= 'index.html'
            if not target.exists():
                problems.append(f'{path.relative_to(site)} -> missing {link}')
            elif url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:
                problems.append(f'{path.relative_to(site)} -> missing anchor {link}')
    for problem in problems[:50]:
        print(problem)
    if problems:
        raise SystemExit(f'{len(problems)} documentation check(s) failed')
    print(f'Content check passed: {len(pages)} HTML pages; local links and anchors valid; English guides and sanitized metadata.')

if __name__ == '__main__':
    main()
