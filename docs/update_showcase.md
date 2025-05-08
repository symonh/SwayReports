# Update Showcase Guide

This document explains how to use the `update_showcase.py` script to manage the Instructor Reports Showcase.

## Basic Usage

By default, the script preserves ALL your manual work:

```bash
python update_showcase.py
```

This will:
- Add any new reports found in the `instructor_reports` directory
- Preserve all existing report data (titles, descriptions, categories)
- Preserve your custom ordering
- Preserve enabled/disabled state of each report
- Create a backup of your showcase file before making changes
- Create a JSON data backup for added safety

## Options

### Refresh Existing Reports

If you want to update information for existing reports from their HTML source files:

```bash
python update_showcase.py --refresh-existing
```

This will:
- Re-extract titles and descriptions from HTML files for all reports
- Re-infer categories for all reports based on HTML content
- Preserve your enabled/disabled settings for each report
- Preserve your custom ordering

### Additional Options

```bash
# Specify a different showcase file
python update_showcase.py --showcase-file path/to/showcase.html

# Specify a different reports directory
python update_showcase.py --reports-dir path/to/reports

# Combine options
python update_showcase.py --refresh-existing --showcase-file path/to/showcase.html
```

## Recovery

If you ever lose your showcase data, you can use the recovery script:

```bash
python recover_showcase_data.py
```

This will:
- Show all available backups (both HTML and JSON)
- Let you choose which backup to recover from
- Restore your categories, ordering, and other custom settings

## When to Use Each Option

- **Default (no options)**: Use when adding new reports or making minor updates. All your manual work is preserved.

- **Refresh Existing (--refresh-existing)**: Use when you've made significant changes to HTML files and want to update the showcase to reflect those changes.

- **Recovery (recover_showcase_data.py)**: Use if you've lost data or want to roll back to a previous version.

## Workflow Examples

### Adding New Reports

1. Place new HTML files in the `instructor_reports` directory
2. Run `python update_showcase.py`
3. New reports will be added with auto-extracted titles, descriptions, and categories
4. Existing reports remain unchanged

### Updating Report Content

1. Edit HTML files in the `instructor_reports` directory
2. Run `python update_showcase.py --refresh-existing`
3. The showcase will update all titles, descriptions, and categories from the HTML files
4. Your ordering and enabled/disabled settings will be preserved

### Recovering from Data Loss

1. Run `python recover_showcase_data.py`
2. Select a backup from the list
3. Your showcase will be restored from the selected backup

## Backup Files

The script creates two types of backups automatically:

1. **HTML Backups**: Complete copies of the showcase HTML file
   - Filename format: `instructor_reports_showcase_YYYYMMDD_HHMMSS_backup.html`

2. **JSON Data Backups**: Structured data of all reports, categories, and ordering
   - Filename format: `instructor_reports_showcase_YYYYMMDD_HHMMSS_data.json`
   - More reliable for recovery as they contain only the essential data

Both backup types can be used with the recovery script. 