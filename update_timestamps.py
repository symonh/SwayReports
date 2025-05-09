import re
import os
from datetime import datetime

# Directory containing the HTML files
REPORTS_DIR = 'instructor_reports'

# Regex to match the old timestamp format
TIMESTAMP_REGEX = re.compile(r'(Last updated: )([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?)')

# Function to convert to the new format
def convert_timestamp(match):
    prefix, old_ts = match.groups()
    try:
        dt = datetime.strptime(old_ts, '%Y-%m-%d %H:%M:%S.%f')
    except ValueError:
        try:
            dt = datetime.strptime(old_ts, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return match.group(0)  # Return unchanged if parsing fails
    # Format: 'May 6, 2025 10:35 PM'
    new_ts = dt.strftime('%b %-d, %Y %-I:%M %p')
    # For systems (like macOS) that don't support %-d and %-I, fallback:
    if '%' in new_ts:
        new_ts = dt.strftime('%b %d, %Y %I:%M %p').replace(' 0', ' ')
    return f'{prefix}{new_ts}'

# Walk through all HTML files in the directory
def process_files():
    for filename in os.listdir(REPORTS_DIR):
        if filename.endswith('.html'):
            path = os.path.join(REPORTS_DIR, filename)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            new_content = TIMESTAMP_REGEX.sub(convert_timestamp, content)
            if new_content != content:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f'Updated: {filename}')

if __name__ == '__main__':
    process_files() 