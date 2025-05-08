#!/usr/bin/env python3
import os
import re
import html
from bs4 import BeautifulSoup

def fix_double_escaped_entities(input_file, output_file=None):
    """
    Fix double-escaped HTML entities in a file.
    If output_file is None, will overwrite the input file.
    """
    if output_file is None:
        output_file = input_file
    
    print(f"Processing {input_file}...")
    
    # Read the file content
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Make a backup of the original file
    backup_file = f"{input_file}.bak"
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Backup created: {backup_file}")
    
    # Fix double-escaped ampersands (&amp;amp;) throughout the file
    fixed_content = re.sub(r'&amp;amp;', '&amp;', content)
    
    # Parse with BeautifulSoup to properly handle HTML structure
    soup = BeautifulSoup(fixed_content, 'html.parser')
    
    # Find and fix content in title and description elements
    for title_div in soup.select('.report-title'):
        if title_div.string:
            # First unescape any HTML entities to get back to plain text
            unescaped_text = html.unescape(title_div.string)
            # Clear and set using our proven method
            title_div.clear()
            # Parse as HTML to maintain the proper escaping
            title_html = BeautifulSoup(f"<span>{unescaped_text}</span>", 'html.parser')
            title_div.append(title_html.span.contents[0])
    
    for desc_div in soup.select('.report-description'):
        if desc_div.string:
            # First unescape any HTML entities to get back to plain text
            unescaped_text = html.unescape(desc_div.string)
            # Clear and set using our proven method
            desc_div.clear()
            # Parse as HTML to maintain the proper escaping
            desc_html = BeautifulSoup(f"<span>{unescaped_text}</span>", 'html.parser')
            desc_div.append(desc_html.span.contents[0])
    
    # Save the fixed content
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    
    print(f"Fixed file saved to: {output_file}")

def check_showcase_file(file_path):
    """Check if the showcase file contains double-escaped entities"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for double-escaped ampersands
    double_amp_count = content.count('&amp;amp;')
    
    print(f"Found {double_amp_count} double-escaped ampersand(s) in {file_path}")
    return double_amp_count > 0

if __name__ == "__main__":
    showcase_file = "instructor_reports_showcase.html"
    
    # Check if the showcase file exists
    if not os.path.exists(showcase_file):
        print(f"Showcase file not found: {showcase_file}")
        exit(1)
    
    # Check if the file needs fixing
    if check_showcase_file(showcase_file):
        print("Double-escaped entities found, fixing file...")
        fix_double_escaped_entities(showcase_file)
        print("Fix completed.")
        
        # Verify the fix
        if check_showcase_file(showcase_file):
            print("Warning: Double-escaped entities still present after fix.")
        else:
            print("Verification: No double-escaped entities found after fix.")
    else:
        print("No double-escaped entities found, no fix needed.")
    
    print("\nTo manually verify, please open the showcase file in a browser and check that all ampersands (&) are displayed correctly.") 