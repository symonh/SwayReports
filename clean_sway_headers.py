#!/usr/bin/env python3
import os
import re
import shutil
from pathlib import Path
from bs4 import BeautifulSoup

def clean_sway_headers(directory):
    """
    Remove only the "Sway Assignment Report Share this assignment with your colleagues" 
    header from instructor reports, without modifying any other content.
    
    Args:
        directory: Path to the directory containing the HTML files
    """
    # Make sure the directory exists
    if not os.path.exists(directory):
        print(f"Directory {directory} not found.")
        return

    # Create a backup directory
    backup_dir = os.path.join(os.path.dirname(directory), "instructor_reports_backup")
    os.makedirs(backup_dir, exist_ok=True)
    print(f"Using backup directory: {backup_dir}")

    # Get all HTML files in the directory
    html_files = [f for f in os.listdir(directory) if f.endswith('.html') and not f.startswith('.')]

    processed_count = 0
    unchanged_count = 0
    
    for filename in html_files:
        file_path = os.path.join(directory, filename)
        backup_path = os.path.join(backup_dir, filename)
        
        # Create a backup of the original file if it doesn't already exist
        if not os.path.exists(backup_path):
            shutil.copy2(file_path, backup_path)
            print(f"Created backup of {filename}")
        
        try:
            # Parse the HTML with BeautifulSoup
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # DEBUG: Print the file size, first and last 1000 characters of the file content
            print(f"\n--- DEBUG: {filename} size: {len(content)} bytes ---")
            print(f"--- DEBUG: Start of {filename} ---\n" + content[:1000] + "\n--- END START DEBUG ---")
            print(f"--- DEBUG: End of {filename} ---\n" + content[-1000:] + "\n--- END END DEBUG ---\n")

            # Check if the specific header text exists in the file
            header_pattern = r'Sway Assignment Report[\s\n]*Share this assignment with your colleagues'
            if not re.search(header_pattern, content, re.IGNORECASE):
                print(f"No header to remove in {filename}, skipping")
                unchanged_count += 1
                continue
            
            # Skip entire <div> blocks by counting nested <div> and </div> tags
            lines = content.splitlines(keepends=True)
            new_lines = []
            i = 0
            header_removed = False
            block_classes = [
                'sway-header-centered',
                'share-banner'
            ]
            while i < len(lines):
                line = lines[i]
                if any('<div' in line and cls in line for cls in block_classes):
                    # Start of a block to remove
                    header_removed = True
                    div_count = line.count('<div') - line.count('</div>')
                    i += 1
                    # Skip lines until all opened divs are closed
                    while i < len(lines) and div_count > 0:
                        div_count += lines[i].count('<div')
                        div_count -= lines[i].count('</div>')
                        i += 1
                    continue  # Skip the closing </div> line too
                else:
                    new_lines.append(line)
                    i += 1
            content = ''.join(new_lines)

            if header_removed:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                processed_count += 1
                print(f"Processed {filename} - removed Sway header and/or share banner")
            else:
                print(f"No header to remove in {filename}, skipping")
                unchanged_count += 1
            
            # DEBUG: Print line number and content for lines containing the target class names
            for idx, line in enumerate(lines):
                if 'sway-header-centered' in line or 'share-banner' in line:
                    print(f"DEBUG: Line {idx}: {line.strip()[:200]}")
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")
    
    print(f"\nProcessed {processed_count} of {len(html_files)} HTML files.")
    print(f"Skipped {unchanged_count} files (no header found or unable to locate).")

if __name__ == "__main__":
    instructor_reports_dir = "instructor_reports"
    clean_sway_headers(instructor_reports_dir) 