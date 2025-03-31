# Sway Reports PDF Converter

A tool to convert HTML instructor reports to paginated PDFs while preserving exact appearance.

## Features

- Converts HTML reports to paginated PDFs
- Preserves exact appearance and styling
- Intelligent pagination (avoids breaking elements like tables and images)
- Customizable page format, margins, and scaling
- Optional headers and footers with page numbers

## Installation

```bash
# Clone the repository
git clone <your-repository-url>
cd SwayReports

# Install dependencies
npm install
```

## Usage

### Basic Usage

```bash
# Convert a single HTML file
node htmlToPdf.js --input html/Report.html

# Convert all HTML files in a directory
node htmlToPdf.js --input html/
```

### Available Options

```
Options:
  --input, -i     Input HTML file or directory                [string] [required]
  --output, -o    Output PDF directory                     [string] [default: "pdfs"]
  --format, -f    Page format                               [string] [default: "A4"]
  --margin, -m    Margins in CSS format (e.g. "1cm")       [string] [default: "1cm"]
  --scale, -s     Scale factor for the page               [number] [default: 1.0]
  --header, -h    Include header                          [boolean] [default: true]
  --footer        Include footer with page numbers        [boolean] [default: true]
  --help          Show help                                                [boolean]
```

### Examples

```bash
# Convert a single file with custom options
node htmlToPdf.js --input html/Report.html --output my-pdfs --format Letter --margin 0.5in --scale 0.9

# Convert all HTML files without headers and footers
node htmlToPdf.js --input html/ --header false --footer false

# Use npm script
npm run convert -- --input html/
```

## How It Works

This tool uses Playwright to render HTML pages exactly as they would appear in a browser, then applies intelligent pagination using CSS print styles. The pagination logic:

1. Prevents page breaks within images, tables, and figures
2. Avoids orphaned or widowed text (prevents single lines at top/bottom of pages)
3. Keeps headings with their following content
4. Preserves all styling, colors, and backgrounds

## Requirements

- Node.js 14+
- Playwright (automatically installed) 