import os
import glob
import re
import sys
import time
import datetime

# Append custom path so config can be imported (if needed)
sys.path.append('/Users/simon/Documents/GitHub')

# Function to extract the generated title from the HTML content.
def extract_generated_title(html):
    match = re.search(r'<div\s+class="generated-title\s+text-info\s+mb-1">(.*?)</div>', html, flags=re.DOTALL)
    if match:
        return match.group(1).strip()
    return None

# Function to extract the completion deadline (UTC) from the HTML content.
def extract_completion_deadline(html):
    pattern = (r'<div\s+class="col-5\s+col-label">\s*Completion deadline:\s*</div>\s*'
               r'<div\s+class="col-7\s+col-value">.*?<span\s+class="utc-time"\s+data-utc-time="([^"]+)"')
    match = re.search(pattern, html, flags=re.DOTALL)
    if match:
        deadline_str = match.group(1).strip()
        try:
            deadline = datetime.datetime.strptime(deadline_str, "%Y-%m-%d %H:%M:%S%z")
            return deadline
        except Exception as e:
            print(f"Error parsing deadline '{deadline_str}':", e)
    return None

# Function to redact instructor information
def redact_instructor_info(html):
    pattern = r'(<div\s+class="col-5\s+col-label">\s*Instructor:\s*</div>\s*<div\s+class="col-7\s+col-value">)([^<]*)(</div>)'
    return re.sub(pattern, r'\1[redacted]\3', html, flags=re.DOTALL)

# Read the entire file and return the content within <body>...</body>
def extract_body(html):
    match = re.search(r"<body[^>]*>(.*?)</body>", html, flags=re.DOTALL|re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return html

def main():
    # Look for all .html files in the "html" folder
    report_files = glob.glob("html/*.html")
    if not report_files:
        print("No .html files found in the 'html' folder.")
        return

    file_info = []
    for filename in report_files:
        print(f"Processing file: {filename}")
        
        # Read the file
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Extract title and deadline before redacting
        title = extract_generated_title(content)
        if not title:
            title = os.path.basename(filename)  # fallback if title not found
        deadline = extract_completion_deadline(content)
        
        # Redact instructor information
        redacted_content = redact_instructor_info(content)
        
        # Write the redacted content back to the same file
        with open(filename, "w", encoding="utf-8") as f:
            f.write(redacted_content)
        
        # Store info for index.html creation
        file_info.append({
            "filename": filename,
            "title": title,
            "deadline": deadline  # may be None if not found
        })
        
        print(f"  Redacted instructor information in {filename}")
        time.sleep(0.2)
    
    # Create an offset-aware maximum datetime for sorting.
    max_dt = datetime.datetime(9999, 12, 31, tzinfo=datetime.timezone.utc)
    file_info.sort(key=lambda x: x["deadline"] if x["deadline"] is not None else max_dt)

    # Build the combined HTML file.
    html_parts = []
    html_parts.append("""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Sway Instructor Reports</title>
  <style>
    html, body {
      height: 100%;
      margin: 0;
      scroll-behavior: smooth;
    }
    body {
      font-family: Arial, sans-serif;
      background-color: #f7f7f7;
      color: #333;
      display: flex;
    }
    /* Sidebar index */
    .sidebar {
      position: fixed;
      top: 0;
      left: 0;
      width: 250px;
      height: 100%;
      background: #fff;
      border-right: 1px solid #ddd;
      overflow-y: auto;
      padding: 20px;
      box-sizing: border-box;
      z-index: 100;
    }
    .sidebar h2 {
      margin-top: 0;
      font-size: 1.2em;
    }
    .sidebar ul {
      list-style-type: none;
      padding: 0;
      margin: 0;
    }
    .sidebar li {
      margin-bottom: 10px;
    }
    .sidebar a {
      text-decoration: none;
      color: #2c3e50;
      font-size: 0.95em;
    }
    .sidebar .deadline {
      font-size: 0.8em;
      color: #777;
    }
    /* Main container for reports */
    .container {
      margin-left: 250px;
      height: 100vh;
      overflow-y: scroll;
      scroll-snap-type: y mandatory;
      width: calc(100% - 250px);
    }
    .report-section {
      scroll-snap-align: start;
      height: 100vh;
      padding: 20px;
      box-sizing: border-box;
      border-bottom: 1px solid #ddd;
      position: relative;
      background: #fff;
    }
    .report-section h2 {
      margin-top: 0;
    }
    .deadline {
      font-size: 0.9em;
      color: #777;
      margin-bottom: 10px;
    }
    iframe {
      width: 100%;
      border: none;
      height: 100%;
    }
  </style>
</head>
<body>
  <div class="sidebar">
    <h2>Index</h2>
    <ul>
""")
    # Create sidebar index entries.
    for info in file_info:
        section_id = os.path.splitext(os.path.basename(info["filename"]))[0]
        html_parts.append(f'      <li><a href="#{section_id}">{info["title"]}</a></li>')
    html_parts.append("    </ul>\n  </div>\n")
    html_parts.append('<div class="container">')
    # Add each report section with iframe pointing to the original file.
    for info in file_info:
        section_id = os.path.splitext(os.path.basename(info["filename"]))[0]
        deadline_str = info["deadline"].strftime("%Y-%m-%d %H:%M:%S %Z") if info["deadline"] else "No deadline"
        html_parts.append(f'<section id="{section_id}" class="report-section">')
        html_parts.append(f'  <h2>{info["title"]}</h2>')
        html_parts.append(f'  <p class="deadline">Deadline: {deadline_str}</p>')
        html_parts.append(f'  <iframe src="{info["filename"]}"></iframe>')
        html_parts.append("</section>")
    html_parts.append("</div>")  # close container
    html_parts.append("</body>\n</html>")
    
    output_filename = "index.html"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write("\n".join(html_parts))
    
    print(f"Successfully redacted instructor information in {len(report_files)} files.")
    print(f"Created {output_filename} that references the files in the html folder.")

if __name__ == "__main__":
    main()