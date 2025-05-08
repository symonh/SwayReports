import os
from bs4 import BeautifulSoup
from pathlib import Path
import html

BACKUP_SHOWCASE = 'instructor_reports_showcase_backup.html'
MAIN_SHOWCASE = 'instructor_reports_showcase.html'
REPORTS_DIR = 'instructor_reports'

def extract_report_info(showcase_file):
    """Extract mapping of filename -> {title, snippet} from a showcase HTML file."""
    with open(showcase_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
    mapping = {}
    for card in soup.select('.report-card'):
        title = card.select_one('.report-title').get_text(strip=True)
        snippet = card.select_one('.report-description').get_text(strip=True)
        link = card.select_one('.view-link')
        if link and 'href' in link.attrs:
            href = link['href']
            filename = os.path.basename(href)
            # Unescape HTML entities
            mapping[filename] = {
                'title': html.unescape(title),
                'snippet': html.unescape(snippet)
            }
    return mapping

def update_showcase(main_showcase, mapping):
    with open(main_showcase, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
    updated = 0
    for card in soup.select('.report-card'):
        link = card.select_one('.view-link')
        if link and 'href' in link.attrs:
            filename = os.path.basename(link['href'])
            if filename in mapping:
                new_title = mapping[filename]['title']
                new_snippet = mapping[filename]['snippet']
                title_div = card.select_one('.report-title')
                desc_div = card.select_one('.report-description')
                if title_div and title_div.get_text(strip=True) != new_title:
                    title_div.string = new_title
                    updated += 1
                if desc_div and desc_div.get_text(strip=True) != new_snippet:
                    desc_div.string = new_snippet
                    updated += 1
    with open(main_showcase, 'w', encoding='utf-8') as f:
        f.write(soup.encode(formatter='minimal').decode())
    print(f"Updated {updated} fields in {main_showcase}")

def update_report_htmls(reports_dir, mapping):
    updated = 0
    for filename, info in mapping.items():
        report_path = Path(reports_dir) / filename
        if not report_path.exists():
            continue
        with open(report_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
        changed = False
        # Update <title>
        if soup.title and soup.title.string != info['title']:
            soup.title.string = info['title']
            changed = True
        # Update first <h1>
        h1 = soup.find('h1')
        if h1 and h1.get_text(strip=True) != info['title']:
            h1.string = info['title']
            changed = True
        # Optionally update a summary/snippet if present (first <p> in #report-content or .markdown-content)
        report_content = soup.find('div', id='report-content')
        if not report_content:
            report_content = soup.find('div', class_='markdown-content')
        if report_content:
            first_p = report_content.find('p')
            if first_p and first_p.get_text(strip=True) != info['snippet']:
                first_p.string = info['snippet']
                changed = True
        if changed:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(soup.encode(formatter='minimal').decode())
            updated += 1
    print(f"Updated {updated} report HTML files")

def main():
    mapping = extract_report_info(BACKUP_SHOWCASE)
    update_showcase(MAIN_SHOWCASE, mapping)
    update_report_htmls(REPORTS_DIR, mapping)

if __name__ == '__main__':
    main() 