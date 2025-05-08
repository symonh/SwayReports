#!/usr/bin/env python3
import os
import re
import shutil
from pathlib import Path
from bs4 import BeautifulSoup

def preprocess_html_files(directory):
    """
    Preprocess HTML files by removing Sway header and social share banner
    sections up to the generated title.
    
    Args:
        directory: Path to the directory containing the HTML files
    """
    # Make sure the directory exists
    if not os.path.exists(directory):
        print(f"Directory {directory} not found.")
        return

    # Create a backup directory
    backup_dir = os.path.join(os.path.dirname(directory), "instructor_reports_backup")
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        print(f"Created backup directory: {backup_dir}")

    # Get all HTML files in the directory
    html_files = [f for f in os.listdir(directory) if f.endswith('.html') and not f.startswith('.')]

    processed_count = 0
    
    for filename in html_files:
        file_path = os.path.join(directory, filename)
        backup_path = os.path.join(backup_dir, filename)
        
        # Create a backup of the original file
        shutil.copy2(file_path, backup_path)
        print(f"Created backup of {filename}")
        
        try:
            # Parse the HTML with BeautifulSoup
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Find the body tag
            body_tag = soup.find('body')
            
            if not body_tag:
                print(f"Could not find body tag in {filename}")
                continue
            
            # Find the generated title
            title_container = soup.find('h1', class_='generated-title')
            
            if not title_container:
                print(f"Could not find generated title in {filename}")
                continue
            
            # Find the row div that contains the title
            row_div = None
            parent = title_container.parent
            while parent and parent.name != 'body':
                if parent.name == 'div' and 'row' in parent.get('class', []):
                    row_div = parent
                    break
                parent = parent.parent
            
            if not row_div:
                print(f"Could not find row div containing title in {filename}")
                continue
            
            # Clear all content in the body up to the row div
            for child in list(body_tag.children):
                if child == row_div:
                    break
                child.extract()
            
            # Fix any remaining issues with the body tag
            body_tag['class'] = []
            if body_tag.has_attr('style'):
                del body_tag['style']
            
            # Write the modified content back to the file
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(str(soup))
            
            processed_count += 1
            print(f"Processed {filename}")
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")
    
    print(f"\nProcessed {processed_count} of {len(html_files)} HTML files.")

if __name__ == "__main__":
    instructor_reports_dir = "/Users/simon/Documents/GitHub/SwayReports/instructor_reports"
    preprocess_html_files(instructor_reports_dir) 