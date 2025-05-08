# SwayReports Architecture

This document describes the architecture and important technical details of the SwayReports project.

## HTML Generation and Handling

### BeautifulSoup HTML Entity Encoding

The application uses BeautifulSoup for HTML parsing and generation. When writing HTML content back to files, we use the `soup.encode(formatter='minimal').decode()` method instead of `str(soup)` to ensure proper preservation of HTML entities.

```python
# Correct way to write BeautifulSoup HTML to files
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(soup.encode(formatter='minimal').decode())
```

This approach prevents issues with HTML entities like `&amp;` being incorrectly re-encoded as `&amp;amp;` when written to files. The `formatter='minimal'` option ensures that only necessary entities are encoded.

## Scripts

### sync_showcase_titles_and_snippets.py

This script synchronizes titles and snippets between the showcase HTML file and individual report HTML files. It ensures consistency in how reports are presented across the application.

The script:
1. Extracts report information from a backup showcase file
2. Updates the main showcase with this information
3. Updates individual report HTML files to match the showcase information

Both the showcase and individual report HTML files use the same encoding method to preserve HTML entities correctly.
