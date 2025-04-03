import os
import glob
import re
import sys
import time
import datetime

# Append custom path so config can be imported (if needed)
sys.path.append('/Users/simon/Documents/GitHub')

# Function to extract the generated title from the HTML content.
# Update this to use a more robust pattern that matches your actual HTML structure
def extract_generated_title(html):
    # First try the original pattern
    match = re.search(r'<div\s+class="generated-title\s+text-info\s+mb-1">(.*?)</div>', html, flags=re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # If that fails, try looking for any h1 or h2 element that might contain the title
    match = re.search(r'<h1[^>]*>(.*?)</h1>', html, flags=re.DOTALL)
    if match:
        return match.group(1).strip()
    
    match = re.search(r'<h2[^>]*>(.*?)</h2>', html, flags=re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # If still no match, try looking for "Assignment Details" section title
    match = re.search(r'<div[^>]*>Assignment Details</div>\s*<div[^>]*>(.*?)</div>', html, flags=re.DOTALL)
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

# Function to modify the HTML structure of individual reports
def modify_report_structure(html, title):
    # Clean the title - replace dashes with spaces and handle colons correctly
    cleaned_title = title.replace("-", " ")
    
    # Handle colons in filenames - they might be encoded as special characters
    if ":" not in cleaned_title:
        # Try to restore colons in places like "Debate", "Ethics", etc. which likely had a colon
        common_title_patterns = [
            "Debate",
            "Ethics",
            "Exploring",
            "Debating",
            "Frontiers",
            "Dimensions of",
            "Worth",
            "A Debate",
            "Norms",
        ]
        
        for pattern in common_title_patterns:
            if pattern in cleaned_title:
                # Make sure to add the colon right after the pattern, not before the next word
                cleaned_title = cleaned_title.replace(pattern, pattern + ":")
                break
    
    # Create CSS for styling
    css_to_add = """
    <style>
    /* Style for our custom title */
    .custom-report-title {
        font-size: 1.75rem;
        font-weight: 600;
        color: #23004D;
        margin: 0 0 15px;
        padding: 15px 15px 0;
        line-height: 1.3;
    }
    
    /* Style for social sharing section */
    .social-sharing {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    </style>
    """
    
    # Insert the CSS before the closing </head> tag
    html = re.sub('</head>', f'{css_to_add}</head>', html, flags=re.IGNORECASE)
    
    # Create the new custom title div
    custom_title_html = f'<div class="custom-report-title">{cleaned_title}</div>'
    
    # Completely replace the card-header with our custom title
    # Match from the opening of card-header to the social sharing section
    html = re.sub(
        r'<div class="card-header">.*?<!-- Social Sharing Buttons - only visible in shared mode -->',
        f'{custom_title_html}\n<!-- Social Sharing Buttons - only visible in shared mode -->', 
        html, 
        flags=re.DOTALL
    )
    
    return html

# New function to add a custom title to the HTML file based on the extracted title
def add_custom_title(html, title):
    # Convert dashes to spaces and clean up the title if it's from a filename
    if "-" in title:
        title = title.replace("-", " ")
    
    # Create a div with the custom title
    custom_title_div = f'<div class="custom-report-title">{title}</div>'
    
    # Insert the custom title right after the opening of the container-fluid
    html = re.sub(r'(<div\s+class="container-fluid"[^>]*>)', 
                  r'\1\n' + custom_title_div, 
                  html, flags=re.DOTALL)
    
    return html

# Read the entire file and return the content within <body>...</body>
def extract_body(html):
    match = re.search(r"<body[^>]*>(.*?)</body>", html, flags=re.DOTALL|re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return html

# Add a debugging function to help understand what's in the HTML
def debug_html_structure(html, filename):
    """Print key parts of the HTML to understand its structure"""
    print(f"\nDebugging HTML structure for {filename}:")
    
    # Look for div elements with class containing "title"
    title_divs = re.findall(r'<div[^>]*class="[^"]*title[^"]*"[^>]*>(.*?)</div>', html, flags=re.DOTALL)
    if title_divs:
        print("Found potential title divs:")
        for i, div in enumerate(title_divs[:3]):  # Show just the first few
            print(f"  {i+1}. {div.strip()[:100]}...")
    else:
        print("No div elements with 'title' in class found.")
    
    # Look for h1/h2 elements
    headers = re.findall(r'<h[12][^>]*>(.*?)</h[12]>', html, flags=re.DOTALL)
    if headers:
        print("Found h1/h2 elements:")
        for i, header in enumerate(headers[:3]):
            print(f"  {i+1}. {header.strip()[:100]}...")
    else:
        print("No h1/h2 elements found.")
    
    # Look for Assignment Details section
    assignment_section = re.search(r'<div[^>]*>Assignment Details</div>\s*<div[^>]*>(.*?)</div>', 
                                  html, flags=re.DOTALL)
    if assignment_section:
        print("Found Assignment Details section:")
        print(f"  Content: {assignment_section.group(1).strip()[:100]}...")
    else:
        print("No Assignment Details section found with expected pattern.")

def main():
    # Look for all .html files in the "html" folder
    report_files = [f for f in glob.glob("html/*.html") if os.path.basename(f) != "index.html"]
    if not report_files:
        print("No .html files found in the 'html' folder.")
        return

    file_info = []
    for filename in report_files:
        print(f"Processing file: {filename}")
        
        # Read the file
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Debug the HTML structure to see what we're working with
        debug_html_structure(content, filename)
        
        # Extract title and deadline before redacting
        title = extract_generated_title(content)
        if not title:
            # Use better fallback - remove file extension and clean up the filename
            base_name = os.path.splitext(os.path.basename(filename))[0]
            # Remove any random hex/id strings at the end
            cleaned_name = re.sub(r'_[0-9a-f]{8,}.*$', '', base_name)
            title = cleaned_name
            print(f"  WARNING: Could not extract title, using cleaned filename: {title}")
        else:
            print(f"  Successfully extracted title: {title}")
            
        deadline = extract_completion_deadline(content)
        
        # Redact instructor information
        redacted_content = redact_instructor_info(content)
        
        # Modify the HTML structure and add custom title in one go
        modified_content = modify_report_structure(redacted_content, title)
        
        # Write the modified content back to the same file
        with open(filename, "w", encoding="utf-8") as f:
            f.write(modified_content)
        
        # Process title for the index
        index_title = title.replace("-", " ")
        # Handle colon restoration for the index too
        if ":" not in index_title:
            for pattern in ["Debate", "Ethics", "Exploring", "Debating", "Frontiers", "Dimensions of", "Worth", "A Debate", "Norms"]:
                if pattern in index_title:
                    index_title = index_title.replace(pattern, pattern + ":")
                    break
        
        # Store info for index.html creation
        file_info.append({
            "filename": filename,
            "title": index_title,
            "deadline": deadline  # may be None if not found
        })
        
        print(f"  Redacted instructor information in {filename}")
        time.sleep(0.2)
    
    # Create an offset-aware maximum datetime for sorting.
    max_dt = datetime.datetime(9999, 12, 31, tzinfo=datetime.timezone.utc)
    file_info.sort(key=lambda x: x["deadline"] if x["deadline"] is not None else max_dt, reverse=True)

    # Build the combined HTML file.
    html_parts = []
    html_parts.append("""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Sway Instructor Reports</title>
  <style>
    :root {
      --bg-color: #f7f7f7;
      --text-color: #333;
      --bg-sidebar: #fff;
      --border-color: #ddd;
      --link-color: #2c3e50;
      --muted-color: #777;
      --container-bg: #fff;
    }
    
    .dark-mode {
      --bg-color: #1a1a1a;
      --text-color: #e6e6e6;
      --bg-sidebar: #252525;
      --border-color: #444;
      --link-color: #88afd3;
      --muted-color: #aaa;
      --container-bg: #2a2a2a;
    }
    
    html, body {
      height: 100%;
      margin: 0;
      scroll-behavior: smooth;
      transition: background-color 0.3s, color 0.3s;
    }
    body {
      font-family: Arial, sans-serif;
      background-color: var(--bg-color);
      color: var(--text-color);
      display: flex;
    }
    /* Sidebar index */
    .sidebar {
      position: fixed;
      top: 0;
      left: 0;
      width: 250px;
      height: 100%;
      background: var(--bg-sidebar);
      border-right: 1px solid var(--border-color);
      overflow-y: auto;
      padding: 20px;
      box-sizing: border-box;
      z-index: 100;
      transition: all 0.3s ease;
    }
    .sidebar.collapsed {
      left: -250px;
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
      color: var(--link-color);
      font-size: 0.95em;
      transition: color 0.3s;
    }
    .sidebar .deadline {
      font-size: 0.8em;
      color: var(--muted-color);
    }
    /* Toggle button for sidebar */
    .sidebar-toggle {
      position: fixed;
      top: 7px; /* Position at half of the header height */
      left: 270px;
      z-index: 101;
      background: var(--container-bg);
      border: 1px solid var(--border-color);
      border-radius: 50%;
      width: 40px;
      height: 40px;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: all 0.3s ease;
      box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .sidebar-toggle.collapsed {
      left: 20px;
    }
    .sidebar-toggle:hover {
      background: var(--bg-color);
    }
    /* Main container for reports */
    .container {
      margin-left: 250px;
      margin-top: 60px; /* Height of the fixed header */
      height: calc(100vh - 60px); /* Subtract header height */
      overflow-y: scroll;
      scroll-snap-type: y mandatory;
      width: calc(100% - 250px);
      transition: margin-left 0.3s ease, width 0.3s ease;
    }
    .container.full-width {
      margin-left: 0;
      width: 100%;
    }
    .report-section {
      scroll-snap-align: start;
      height: 100vh;
      padding: 20px;
      box-sizing: border-box;
      border-bottom: 1px solid var(--border-color);
      position: relative;
      background: var(--container-bg);
      transition: background-color 0.3s;
    }
    .report-section h2 {
      margin-top: 0;
    }
    
    /* Report assignment title styling */
    .report-assignment-title {
      position: relative;
      display: flex;
      align-items: center;
      height: 60px;
      margin-bottom: 15px;
      padding: 0 10px;
      background-color: var(--container-bg);
      border-radius: 5px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
      z-index: 5;
    }
    
    .report-assignment-title h3 {
      margin: 0;
      color: #23004D;
      font-size: 1.4rem;
      font-weight: 500;
      line-height: 1.3;
    }
    
    .dark-mode .report-assignment-title h3 {
      color: #bb86fc;
    }
    
    iframe {
      width: 100%;
      border: none;
      height: calc(100% - 75px); /* Adjust for title height */
      background: var(--container-bg);
    }
    
    /* Night mode toggle */
    .mode-toggle {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      padding-bottom: 10px;
      border-bottom: 1px solid var(--border-color);
    }
    
    .switch {
      position: relative;
      display: inline-block;
      width: 50px;
      height: 24px;
    }
    
    .switch input {
      opacity: 0;
      width: 0;
      height: 0;
    }
    
    .slider {
      position: absolute;
      cursor: pointer;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background-color: #ccc;
      transition: .4s;
      border-radius: 24px;
    }
    
    .slider:before {
      position: absolute;
      content: "";
      height: 16px;
      width: 16px;
      left: 4px;
      bottom: 4px;
      background-color: white;
      transition: .4s;
      border-radius: 50%;
    }
    
    input:checked + .slider {
      background-color: #2196F3;
    }
    
    input:checked + .slider:before {
      transform: translateX(26px);
    }

    /* Fixed header with the main title */
    .fixed-header {
      position: fixed;
      top: 0;
      left: 250px; /* Same as sidebar width */
      right: 0;
      background: var(--container-bg);
      z-index: 99;
      border-bottom: 1px solid var(--border-color);
      transition: left 0.3s ease;
      display: flex;
      align-items: center;
      padding: 0 15px 0 80px; /* Added left padding to prevent overlap with toggle button */
    }
    
    .fixed-header.full-width {
      left: 0;
      padding-left: 80px; /* Increased left padding when sidebar is collapsed */
    }

    .fixed-header h1 {
      color: #23004D;
      margin: 0;
      padding: 15px 0;
      font-size: 24px;
    }

    .dark-mode .fixed-header h1 {
      color: #bb86fc !important; /* Light purple in dark mode */
    }
  </style>
</head>
<body>
  <div class="sidebar">
    <div class="mode-toggle">
      <span>Night Mode</span>
      <label class="switch">
        <input type="checkbox" id="darkModeToggle">
        <span class="slider"></span>
      </label>
    </div>
    <h2>Index</h2>
    <ul>
""")
    # Create sidebar index entries.
    for info in file_info:
        section_id = os.path.splitext(os.path.basename(info["filename"]))[0]
        html_parts.append(f'      <li><a href="#{section_id}">{info["title"]}</a></li>')
    html_parts.append("    </ul>\n  </div>\n")

    # Add the sidebar toggle button
    html_parts.append('''
  <div class="sidebar-toggle">
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="toggle-icon">
      <polyline points="15 18 9 12 15 6"></polyline>
    </svg>
  </div>
    ''')

    # Add the new heading in a fixed header div before the container
    html_parts.append('''
      <div class="fixed-header">
        <img src="sway-logo.png" alt="Sway Logo" style="height:40px; margin-right: 15px;">
        <h1>Instructor Reports From Real Sway Chats</h1>
      </div>
    ''')

    html_parts.append('<div class="container">')
    # Add each report section with iframe pointing to the original file.
    for info in file_info:
        section_id = os.path.splitext(os.path.basename(info["filename"]))[0]
        html_parts.append(f'<section id="{section_id}" class="report-section">')
        html_parts.append(f'  <div class="report-assignment-title">')
        html_parts.append(f'    <h3>{info["title"]}</h3>')
        html_parts.append(f'  </div>')
        html_parts.append(f'  <iframe src="{info["filename"]}" class="report-iframe" data-src="{info["filename"]}"></iframe>')
        html_parts.append("</section>")
    html_parts.append("</div>")  # close container
    
    # Add JavaScript for dark mode functionality
    html_parts.append("""
  <script>
    // Dark mode toggle functionality
    const darkModeToggle = document.getElementById('darkModeToggle');
    const body = document.body;
    
    // More reliable approach to apply dark mode to iframes
    function applyDarkModeToIframes(isDarkMode) {
      // Add a style tag directly to each HTML file loaded in the iframe
      const iframes = document.querySelectorAll('.report-iframe');
      
      iframes.forEach(iframe => {
        // Get the base src
        const baseSrc = iframe.getAttribute('data-src');
        
        // Update iframe src with or without dark mode parameter
        if (isDarkMode) {
          iframe.src = baseSrc + (baseSrc.includes('?') ? '&' : '?') + 'darkmode=true&timestamp=' + new Date().getTime();
        } else {
          iframe.src = baseSrc + (baseSrc.includes('?') ? '&' : '?') + 'timestamp=' + new Date().getTime();
        }
      });
    }
    
    // Function to toggle dark mode
    function toggleDarkMode(isDarkMode) {
      if (isDarkMode) {
        body.classList.add('dark-mode');
        localStorage.setItem('darkMode', 'enabled');
      } else {
        body.classList.remove('dark-mode');
        localStorage.setItem('darkMode', 'disabled');
      }
      
      // Apply dark mode to iframes
      applyDarkModeToIframes(isDarkMode);
    }
    
    // Check for saved preference
    const isDarkModeEnabled = localStorage.getItem('darkMode') === 'enabled';
    
    // Set initial state
    if (isDarkModeEnabled) {
      darkModeToggle.checked = true;
      body.classList.add('dark-mode');
    }
    
    // Apply to iframes when page has fully loaded
    window.addEventListener('load', function() {
      if (isDarkModeEnabled) {
        applyDarkModeToIframes(true);
      }
    });
    
    // Toggle dark mode on change
    darkModeToggle.addEventListener('change', function() {
      toggleDarkMode(this.checked);
    });
    
    // Sidebar toggle functionality
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    const container = document.querySelector('.container');
    const fixedHeader = document.querySelector('.fixed-header');
    
    // Check for saved sidebar state
    const isSidebarCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
    
    // Set initial sidebar state
    if (isSidebarCollapsed) {
      sidebar.classList.add('collapsed');
      sidebarToggle.classList.add('collapsed');
      container.classList.add('full-width');
      fixedHeader.classList.add('full-width');
    }
    
    // Toggle sidebar on click
    sidebarToggle.addEventListener('click', function() {
      sidebar.classList.toggle('collapsed');
      sidebarToggle.classList.toggle('collapsed');
      container.classList.toggle('full-width');
      fixedHeader.classList.toggle('full-width');
      
      // Update the toggle icon direction
      const toggleIcon = sidebarToggle.querySelector('.toggle-icon');
      if (sidebar.classList.contains('collapsed')) {
        // Change to right arrow when sidebar is collapsed
        toggleIcon.innerHTML = '<polyline points="9 18 15 12 9 6"></polyline>';
      } else {
        // Change to left arrow when sidebar is expanded
        toggleIcon.innerHTML = '<polyline points="15 18 9 12 15 6"></polyline>';
      }
      
      // Save preference
      localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
    });
    
    // Update the toggle icon based on initial state
    const toggleIcon = sidebarToggle.querySelector('.toggle-icon');
    if (isSidebarCollapsed) {
      toggleIcon.innerHTML = '<polyline points="9 18 15 12 9 6"></polyline>';
    }
  </script>""")

    # Now inject the dark mode handler script into each HTML file as well
    for filename in report_files:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Completely new approach for dark mode in iframes
        # Replace with a more robust dark mode solution
        if "</head>" in content:
            # Add dark mode detector to the head section
            head_script = """
<script>
  // Detect dark mode from URL parameter
  function isDarkModeEnabled() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('darkmode') === 'true';
  }

  // Initialize dark mode if needed
  if (isDarkModeEnabled()) {
    // Add immediate style to prevent flash of light content
    document.documentElement.style.backgroundColor = '#1a1a1a';
    document.documentElement.style.color = '#e6e6e6';
  }
</script>

<style id="darkmode-styles">
  /* Dark mode styles will be enabled via JavaScript */
</style>
</head>"""
            content = content.replace("</head>", head_script)
        
        # Add the thorough dark mode script before the closing body tag
        if "</body>" in content:
            body_script = """
<script>
  // Dark mode implementation
  (function() {
    // Only apply if the darkmode parameter is true
    if (!isDarkModeEnabled()) return;
    
    // Get our style element
    const darkStyles = document.getElementById('darkmode-styles');
    
    // Set comprehensive dark mode styles
    darkStyles.textContent = `
      /* Force literally everything to dark mode */
      html, body { 
        background-color: #1a1a1a !important;
        color: #e6e6e6 !important;
      }
      
      /* Target ALL elements with a wildcard selector */
      * {
        background-color: transparent !important;
        border-color: #444 !important;
      }
      
      /* Explicitly target common containers */
      div, section, article, aside, header, footer, main, nav,
      .container, .row, .col, .card, .panel, .jumbotron, .well,
      [class*="container"], [class*="wrapper"], [class*="panel"], 
      [class*="card"], [class*="box"], [class*="section"],
      [id*="container"], [id*="wrapper"], [id*="panel"], 
      [id*="card"], [id*="box"], [id*="section"] {
        background-color: #2a2a2a !important;
        color: #e6e6e6 !important;
        border-color: #444 !important;
      }
      
      /* Force background colors for specific elements */
      [class*="bg-"], [class*="background"], 
      [style*="background"], [style*="bg"] {
        background-color: #2a2a2a !important;
      }
      
      /* White elements and their children */
      [class*="white"], [class*="light"],
      [style*="white"], [style*="rgb(255"], [style*="rgb(248"],
      [style*="rgb(250"], [style*="rgb(252"], [style*="rgb(240"],
      [style*="rgb(245"], [style*="#fff"], [style*="#ffffff"] {
        background-color: #2a2a2a !important;
        color: #e6e6e6 !important;
      }
      
      /* Bootstrap and common framework classes */
      .bg-white, .bg-light, .bg-default, .bg-secondary,
      .text-dark, .text-black {
        background-color: #2a2a2a !important;
        color: #e6e6e6 !important;
      }
      
      /* Links */
      a, a:visited, a:hover, a:active, .link, [class*="link"] {
        color: #88afd3 !important;
      }
      
      /* Code and pre elements */
      pre, code, .code, .pre, [class*="code"], [class*="pre"] {
        background-color: #333 !important;
        color: #f8f8f8 !important;
      }
      
      /* Tables */
      table, tr, td, th, thead, tbody, tfoot,
      .table, [class*="table"] {
        background-color: #2a2a2a !important;
        color: #e6e6e6 !important;
        border-color: #444 !important;
      }
      
      /* Form elements */
      input, textarea, select, button, .form-control,
      [class*="input"], [class*="button"], [class*="form"] {
        background-color: #333 !important;
        color: #e6e6e6 !important;
        border-color: #555 !important;
      }
      
      /* Modals and popups */
      .modal, .popover, .tooltip, .dropdown-menu,
      [class*="modal"], [class*="popover"], [class*="tooltip"], [class*="dropdown"] {
        background-color: #2a2a2a !important;
        color: #e6e6e6 !important;
        border-color: #444 !important;
      }
      
      /* Sway specific elements observed in screenshot */
      [class*="assignment-details"], [class*="details"],
      .card-like, .topic-section, [class*="topic"],
      [class*="student"], [class*="discuss"], [class*="debate"],
      [class*="abortion"], [class*="timeline"],
      .marquis, .hendricks, .thomson, .singer,
      .guide, .completion {
        background-color: #2a2a2a !important;
        color: #e6e6e6 !important;
      }
      
      /* Specific elements in the screenshot */
      .students-discuss, .student-debate, .debate-section,
      [class*="discuss"], [class*="debate"], 
      [style*="background-color: rgb(255, 255, 255)"] {
        background-color: #2a2a2a !important;
        color: #e6e6e6 !important;
      }

      /* General text colors and backgrounds */
      h1, h2, h3, h4, h5, h6, p, span, li, strong, em, b, i, u,
      label, small, .text, [class*="text"] {
        color: #e6e6e6 !important;
      }
      
      /* Target RGB inline styles specifically */
      [style*="rgb("] {
        background-color: #2a2a2a !important;
        color: #e6e6e6 !important;
      }
      
      /* Override any !important inline styles with double !important (hack but effective) */
      [style*="!important"] {
        background-color: #2a2a2a !important !important;
        color: #e6e6e6 !important !important;
      }
      
      /* Fix for dark purple text against dark background */
      h1, h2, h3, h4, h5, h6, 
      [style*="purple"], [style*="violet"], 
      [class*="purple"], [class*="violet"],
      [style*="rgb(128, 0, 128)"], [style*="rgb(138, 43, 226)"],
      [style*="rgb(75, 0, 130)"], [style*="rgb(106, 90, 205)"],
      [style*="rgb(147, 112, 219)"], [style*="rgb(153, 50, 204)"],
      [style*="color: #800080"], [style*="color: #8a2be2"],
      [style*="color: #4b0082"], [style*="color: #6a5acd"] {
        color: #bb86fc !important; /* Light purple that works on dark backgrounds */
      }
      
      /* Specific fix for topic headers and main title */
      .generated-title, [class*="title"],
      [id*="topic"], [class*="topic"],
      [id*="marquis"], [class*="marquis"],
      [id*="hendricks"], [class*="hendricks"],
      [id*="thomson"], [class*="thomson"],
      [id*="singer"], [class*="singer"],
      [id*="abortion"], [class*="abortion"] {
        color: #bb86fc !important; /* Light purple */
      }

      /* Add specific targeting for the #23004D dark purple color */
      [style*="color: #23004D"], [style*="color:#23004D"],
      [style*="color: rgb(35, 0, 77)"], [style*="color:rgb(35, 0, 77)"],
      [style*="color: rgba(35, 0, 77"], [style*="color:rgba(35, 0, 77"],
      [class*="text-primary"], /* Common bootstrap class that might use this color */
      .assignment-details h1 + div, /* Target divs immediately after headings in assignment details */
      .topic-list span, /* Target spans in topic lists */
      .topic-container * /* Target all elements in topic containers */
      {
        color: #bb86fc !important; /* Light purple for readability */
      }
    `;
    
    // Function to force dark backgrounds on elements that resist
    function forceDarkElements() {
      // Get all elements
      const allElements = document.querySelectorAll('*');
      
      // Check the computed style of all elements
      allElements.forEach(el => {
        const style = window.getComputedStyle(el);
        const bgColor = style.backgroundColor;
        const textColor = style.color;
        
        // If it's still white or very light (rgb values close to 255)
        if (bgColor.includes('rgb(255, 255, 255)') || 
            bgColor.includes('rgb(248') ||
            bgColor.includes('rgb(250') ||
            bgColor.includes('rgb(252') ||
            bgColor.includes('rgb(245')) {
          // Force it to be dark with inline style (highest specificity)
          el.style.setProperty('background-color', '#2a2a2a', 'important');
          el.style.setProperty('color', '#e6e6e6', 'important');
        }
        
        // Check for dark purple text that would be hard to read
        if (textColor.includes('rgb(128, 0, 128)') || // purple
            textColor.includes('rgb(75, 0, 130)') ||  // indigo
            textColor.includes('rgb(106, 90, 205)') || // slate blue
            textColor.includes('rgb(138, 43, 226)') || // blue violet
            textColor.includes('rgb(147, 112, 219)') || // medium purple
            textColor.includes('rgb(153, 50, 204)') || // dark orchid
            textColor.includes('rgb(102, 51, 153)') || // rebecca purple
            (textColor.includes('rgb(') && 
             parseInt(textColor.match(/\d+/g)[0]) < 150 && 
             parseInt(textColor.match(/\d+/g)[1]) < 100 && 
             parseInt(textColor.match(/\d+/g)[2]) > 150)) { // Any dark purplish color
          
          // Replace with a lighter purple that's readable on dark backgrounds
          el.style.setProperty('color', '#bb86fc', 'important'); // Material Design purple
        }

        // Add specific check for the #23004D dark purple
        if (textColor === 'rgb(35, 0, 77)' || 
            textColor.includes('#23004D') ||
            (textColor.includes('rgb(') && 
             parseInt(textColor.match(/\d+/g)[0]) === 35 && 
             parseInt(textColor.match(/\d+/g)[1]) === 0 && 
             parseInt(textColor.match(/\d+/g)[2]) === 77)) {
          
          // Replace with a lighter purple that's readable on dark backgrounds
          el.style.setProperty('color', '#bb86fc', 'important');
        }
      });
    }
    
    // Run once when loaded
    document.addEventListener('DOMContentLoaded', function() {
      forceDarkElements();
      
      // And again after all images and resources load
      window.addEventListener('load', forceDarkElements);
      
      // And periodically check for any dynamic content
      setInterval(forceDarkElements, 1000);
    });
  })();
</script>
</body>"""
            content = content.replace("</body>", body_script)
            
            # Write the updated content back to the file
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
    
    output_filename = "index.html"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write("\n".join(html_parts))
    
    print(f"Successfully redacted instructor information in {len(report_files)} files.")
    print(f"Created {output_filename} that references the files in the html folder.")

if __name__ == "__main__":
    main()