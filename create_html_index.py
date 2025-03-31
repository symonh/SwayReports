import os
import glob
import re

def extract_generated_title(html):
    # First try the original pattern
    match = re.search(r'<div\s+class="generated-title\s+text-info\s+mb-1">(.*?)</div>', html, flags=re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # If that fails, try looking for any h1 or h2 element
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

def main():
    # Create html directory if it doesn't exist
    os.makedirs("html", exist_ok=True)
    
    # Look for all .html files in the "html" folder
    html_files = glob.glob("html/*.html")
    if not html_files:
        print("No .html files found in the 'html' folder.")
        return

    file_info = []
    for filename in html_files:
        # Read the file to extract title
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Extract title
        title = extract_generated_title(content)
        if not title:
            # Use filename as fallback
            base_name = os.path.splitext(os.path.basename(filename))[0]
            # Remove any random hex/id strings at the end
            cleaned_name = re.sub(r'_[0-9a-f]{8,}.*$', '', base_name)
            # Replace underscores with spaces
            cleaned_name = cleaned_name.replace('_', ' ')
            title = cleaned_name
        
        file_info.append({
            "filename": os.path.basename(filename),
            "title": title
        })
    
    # Sort files alphabetically by title
    file_info.sort(key=lambda x: x["title"])
    
    # Build the HTML file
    html_parts = []
    html_parts.append("""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Sway Reports Directory</title>
  <style>
    :root {
      --bg-color: #f7f7f7;
      --text-color: #333;
      --bg-container: #fff;
      --border-color: #ddd;
      --link-color: #2c3e50;
      --muted-color: #777;
      --success-color: #4CAF50;
    }
    
    body {
      font-family: Arial, sans-serif;
      background-color: var(--bg-color);
      color: var(--text-color);
      line-height: 1.6;
      max-width: 800px;
      margin: 0 auto;
      padding: 20px;
    }
    
    h1 {
      color: #23004D;
      text-align: center;
      margin-bottom: 30px;
    }
    
    .container {
      background-color: var(--bg-container);
      border-radius: 8px;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
      padding: 20px;
    }
    
    .file-list {
      list-style-type: none;
      padding: 0;
    }
    
    .file-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 15px;
      border-bottom: 1px solid var(--border-color);
      transition: background-color 0.2s;
    }
    
    .file-item:last-child {
      border-bottom: none;
    }
    
    .file-item:hover {
      background-color: rgba(0, 0, 0, 0.02);
    }
    
    .file-link {
      color: var(--link-color);
      text-decoration: none;
      flex: 1;
    }
    
    .file-link:hover {
      text-decoration: underline;
    }
    
    .copy-button {
      background-color: #f1f1f1;
      border: none;
      border-radius: 4px;
      padding: 5px 10px;
      cursor: pointer;
      font-size: 14px;
      transition: background-color 0.2s;
    }
    
    .copy-button:hover {
      background-color: #e3e3e3;
    }
    
    .copy-button.copied {
      background-color: var(--success-color);
      color: white;
    }
    
    .back-link {
      display: block;
      text-align: center;
      margin-top: 20px;
      color: var(--link-color);
      text-decoration: none;
    }
    
    .back-link:hover {
      text-decoration: underline;
    }
  </style>
</head>
<body>
  <h1>Sway Reports Directory</h1>
  
  <div class="container">
    <ul class="file-list">
""")

    # Add list items with links and copy buttons
    for info in file_info:
        filename = info["filename"]
        title = info["title"]
        absolute_url = f"https://symonh.github.io/SwayReports/html/{filename}"
        
        html_parts.append(f"""      <li class="file-item">
        <a href="{filename}" class="file-link">{title}</a>
        <button class="copy-button" data-url="{absolute_url}">Copy Link</button>
      </li>""")
    
    html_parts.append("""    </ul>
  </div>
  
  <a href="../index.html" class="back-link">Back to Main Reports Page</a>

  <script>
    // Add copy to clipboard functionality
    document.querySelectorAll('.copy-button').forEach(button => {
      button.addEventListener('click', () => {
        const url = button.getAttribute('data-url');
        
        // Create a temporary input element
        const tempInput = document.createElement('input');
        tempInput.value = url;
        document.body.appendChild(tempInput);
        
        // Select and copy the link
        tempInput.select();
        document.execCommand('copy');
        
        // Remove the temporary input
        document.body.removeChild(tempInput);
        
        // Visual feedback
        button.textContent = 'Copied!';
        button.classList.add('copied');
        
        // Reset button text after 2 seconds
        setTimeout(() => {
          button.textContent = 'Copy Link';
          button.classList.remove('copied');
        }, 2000);
      });
    });
  </script>
</body>
</html>""")

    # Write the HTML file
    output_path = os.path.join("html", "index.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(html_parts))
    
    print(f"Successfully created {output_path} with links to {len(html_files)} reports.")

if __name__ == "__main__":
    main() 