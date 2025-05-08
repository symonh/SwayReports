import os
from bs4 import BeautifulSoup
import subprocess
import shutil

def test_ampersand_display():
    # Setup: copy backup to a temp showcase file
    shutil.copyfile('instructor_reports_showcase_backup.html', 'test_showcase.html')
    # Patch the script to use the test file
    with open('scripts/sync_showcase_titles_and_snippets.py', 'r', encoding='utf-8') as f:
        script = f.read()
    script = script.replace('MAIN_SHOWCASE = \'instructor_reports_showcase.html\'', 'MAIN_SHOWCASE = \'test_showcase.html\'')
    with open('scripts/sync_showcase_titles_and_snippets_test.py', 'w', encoding='utf-8') as f:
        f.write(script)
    # Run the patched script
    subprocess.run(['python', 'scripts/sync_showcase_titles_and_snippets_test.py'], check=True)
    # Check the output
    with open('test_showcase.html', 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
    for card in soup.select('.report-card'):
        title = card.select_one('.report-title').get_text()
        assert '&amp;' not in title, f"Title still contains &amp;: {title}"
        desc = card.select_one('.report-description').get_text()
        assert '&amp;' not in desc, f"Description still contains &amp;: {desc}"
    print('Test passed: No &amp; in titles or descriptions')
    # Cleanup
    os.remove('test_showcase.html')
    os.remove('scripts/sync_showcase_titles_and_snippets_test.py') 