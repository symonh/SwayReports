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
        
        # Extract information before redacting
        title = extract_generated_title(content)
        if not title:
            title = os.path.basename(filename)  # fallback if title not found
        deadline = extract_completion_deadline(content)
        
        # Redact instructor information
        redacted_content = redact_instructor_info(content)
        
        # Write the redacted content back to the same file
        with open(filename, "w", encoding="utf-8") as f:
            f.write(redacted_content)
        
        # Store the file info for creating the index
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
    
    # Build the index.html file
    create_index_html(file_info)
    
    print(f"Successfully redacted instructor information in {len(report_files)} files.")
    print("Created index.html file that links to files in the html folder.")

def create_index_html(file_info):
    html_parts = []
    html_parts.append("""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Instructor Reports</title>
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
      margin-bottom: 15px;
    }
    .sidebar a {
      text-decoration: none;
      color: #2c3e50;
      font-size: 0.95em;
      display: block;
      padding: 5px;
      border-radius: 4px;
      transition: background-color 0.2s;
    }
    .sidebar a:hover {
      background-color: #f0f0f0;
    }
    .sidebar .deadline {
      font-size: 0.8em;
      color: #777;
      margin-top: 3px;
    }
    /* Main container */
    .container {
      margin-left: 250px;
      padding: 30px;
      box-sizing: border-box;
      width: calc(100% - 250px);
    }
    .header {
      margin-bottom: 30px;
    }
    .report-list {
      list-style-type: none;
      padding: 0;
    }
    .report-item {
      background: #fff;
      border-radius: 8px;
      box-shadow: 0 2px 5px rgba(0,0,0,0.1);
      margin-bottom: 20px;
      padding: 20px;
    }
    .report-item h3 {
      margin-top: 0;
      color: #2c3e50;
    }
    .report-item .deadline {
      font-size: 0.9em;
      color: #777;
      margin-bottom: 15px;
    }
    .report-item a {
      display: inline-block;
      background-color: #4a6fa5;
      color: white;
      padding: 8px 16px;
      text-decoration: none;
      border-radius: 4px;
      transition: background-color 0.2s;
    }
    .report-item a:hover {
      background-color: #3a5a80;
    }
  </style>
</head>
<body>
  <div class="sidebar">
    <h2>Reports Index</h2>
    <ul>
""")
    # Create sidebar index entries
    for info in file_info:
        relative_path = info["filename"]  # Should be like "html/filename.html"
        filename_only = os.path.basename(relative_path)
        deadline_str = info["deadline"].strftime("%Y-%m-%d %H:%M:%S %Z") if info["deadline"] else "No deadline"
        html_parts.append(f'      <li><a href="{relative_path}">{info["title"]}</a><div class="deadline">({deadline_str})</div></li>')
    
    html_parts.append("    </ul>\n  </div>\n")
    html_parts.append('<div class="container">')
    html_parts.append('  <div class="header">')
    html_parts.append('    <h1>Instructor Reports</h1>')
    html_parts.append('    <p>Select a report from the sidebar or from the list below.</p>')
    html_parts.append('  </div>')
    html_parts.append('  <ul class="report-list">')
    
    # Add main content list items
    for info in file_info:
        relative_path = info["filename"]  # Should be like "html/filename.html"
        deadline_str = info["deadline"].strftime("%Y-%m-%d %H:%M:%S %Z") if info["deadline"] else "No deadline"
        html_parts.append('    <li class="report-item">')
        html_parts.append(f'      <h3>{info["title"]}</h3>')
        html_parts.append(f'      <div class="deadline">Deadline: {deadline_str}</div>')
        html_parts.append(f'      <a href="{relative_path}">View Report</a>')
        html_parts.append('    </li>')
    
    html_parts.append('  </ul>')
    html_parts.append('</div>')
    html_parts.append('</body>\n</html>')
    
    # Write the index.html file
    with open("index.html", "w", encoding="utf-8") as f:
        f.write("\n".join(html_parts))

if __name__ == "__main__":
    main()