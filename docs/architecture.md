# SwayReports Architecture

This document describes the architecture and important technical details of the SwayReports project.

## HTML Generation and Handling

### BeautifulSoup HTML Entity Encoding

The application uses BeautifulSoup for HTML parsing and generation. While the application previously used the `soup.encode(formatter='minimal').decode()` method, we've now implemented a more robust approach for handling HTML entities, particularly ampersands.

#### Legacy Approach (Has Issues)

```python
# Old way to write BeautifulSoup HTML to files - has issues with double escaping
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(soup.encode(formatter='minimal').decode())
```

#### Improved HTML Entity Handling

Our improved solution addresses issues with HTML entities like `&amp;` being incorrectly re-encoded as `&amp;amp;` when written to files:

```python
# Reading content with html.unescape to handle existing entities
title = html.unescape(element.get_text().strip())

# Writing content properly
title_div = soup.new_tag('div')
title_div.clear()
title_html = BeautifulSoup(f"<span>{title}</span>", 'html.parser')
title_div.append(title_html.span.contents[0])
```

This approach:
1. Uses `html.unescape()` when reading text to convert any entities to their character equivalents
2. Creates a temporary HTML fragment when setting text to ensure proper entity handling
3. Appends the content nodes rather than setting string values, which prevents double-escaping

After extensive testing, this approach correctly preserves ampersands and other special characters throughout the HTML generation pipeline.

## Scripts

### category_manager.py and update_showcase.py

These scripts both implement the improved HTML entity handling to ensure ampersands and other special characters are displayed correctly in the browser.

### fix_showcase_ampersands.py

This utility script can fix any double-escaped entities in existing showcase files. It:
1. Makes a backup of the original file
2. Finds and corrects any double-escaped ampersands (`&amp;amp;` → `&amp;`)
3. Rewrites all content using the improved entity handling approach

### sync_showcase_titles_and_snippets.py

This script synchronizes titles and snippets between the showcase HTML file and individual report HTML files. It ensures consistency in how reports are presented across the application.

The script:
1. Extracts report information from a backup showcase file
2. Updates the main showcase with this information
3. Updates individual report HTML files to match the showcase information
