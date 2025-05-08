#!/usr/bin/env python3
import os
import re
import random
import html
import json
import shutil
import argparse
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup

def extract_title_and_categories(html_file):
    """
    Extract the title and infer categories based on the filename and content.
    Only used for NEW reports that don't exist in the showcase yet.
    
    Args:
        html_file: Path to HTML file
    
    Returns:
        Tuple of (title, categories)
    """
    # Default categories if we can't infer any
    default_categories = ["ethics"]
    
    try:
        with open(html_file, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Extract title
        title_match = re.search(r'<h1\s+class="generated-title">\s*(.*?)\s*</h1>', content, re.DOTALL)
        if title_match:
            title = title_match.group(1).strip()
        else:
            # Use filename as fallback
            title = os.path.basename(html_file).replace('.html', '').replace('-', ' ')
            
        # Infer categories from title and content
        categories = default_categories.copy()
        
        # Keywords for different categories
        category_keywords = {
            "healthcare": ["health", "hospital", "patient", "medical", "doctor", "care", "treatment", "therapy", "illness", "disease"],
            "science": ["science", "scientific", "research", "biology", "physics", "chemistry", "species", "evolution", "genetic"],
            "philosophy": ["philosophy", "philosophical", "ethics", "moral", "value", "virtue", "principle", "duty", "utilitarianism", "deontology", "morality"],
            "bioethics": ["bioethics", "abortion", "euthanasia", "clone", "genetic engineering", "enhancement", "reproductive"],
            "environment": ["environment", "climate", "ecology", "conservation", "species", "extinction", "habitat", "animal", "sustainability"],
            "social-issues": ["social", "society", "community", "inequality", "justice", "discrimination", "policy", "politics", "economic", "poverty"]
        }
        
        # Check title and content for keywords
        lowercase_title = title.lower()
        lowercase_content = content.lower()
        
        for category, keywords in category_keywords.items():
            for keyword in keywords:
                if keyword.lower() in lowercase_title or keyword.lower() in lowercase_content[:10000]:  # Only search first part of content
                    if category not in categories:
                        categories.append(category)
                    break
                        
        return title, categories
    
    except Exception as e:
        print(f"Error processing {html_file}: {e}")
        return os.path.basename(html_file).replace('.html', '').replace('-', ' '), default_categories

def extract_first_paragraph(html_file):
    """
    Extract the first paragraph from the instructor report,
    limiting to 50 words plus the remainder of the current sentence, followed by ellipsis.
    
    Args:
        html_file: Path to HTML file
    
    Returns:
        String containing the truncated first paragraph text, or a default message if not found
    """
    try:
        with open(html_file, 'r', encoding='utf-8') as file:
            content = file.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Look for the report content div
        report_content = soup.find('div', id='report-content', class_='markdown-content')
        
        # If not found, try alternative selectors
        if not report_content:
            report_content = soup.find('div', id='report-content')
        
        if not report_content:
            report_content = soup.find('div', class_='markdown-content')
        
        if report_content:
            # Find the first paragraph
            first_paragraph = report_content.find('p')
            
            if first_paragraph:
                text = first_paragraph.get_text().strip()
                
                # Process the text to limit to 50 words + remainder of sentence
                words = text.split()
                
                if len(words) <= 50:
                    # If the paragraph is less than 50 words, return it all
                    return text
                
                # Get the first 50 words
                truncated_text = ' '.join(words[:50])
                
                # Find the end of the current sentence after 50 words
                remaining_text = ' '.join(words[50:])
                sentence_end_match = re.search(r'^(.*?[.!?])', remaining_text)
                
                if sentence_end_match:
                    # Add the remainder of the current sentence
                    truncated_text += ' ' + sentence_end_match.group(1)
                
                # Add ellipsis
                truncated_text += '...'
                
                return truncated_text
        
        # Fall back to a default description if we couldn't find the paragraph
        return "Instructor report for this assignment."
        
    except Exception as e:
        print(f"Error extracting paragraph from {html_file}: {e}")
        return "Instructor report for this assignment."

def extract_existing_reports_data(showcase_file):
    """
    Extract existing reports' data from the showcase file.
    This preserves categories, order, and other custom settings.
    
    Args:
        showcase_file: Path to the showcase HTML file
        
    Returns:
        Dictionary of filename -> report data
    """
    if not os.path.exists(showcase_file):
        return {}
        
    try:
        with open(showcase_file, 'r', encoding='utf-8') as file:
            content = file.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        existing_reports = {}
        report_order = []
        
        # Extract all categories first
        all_categories = []
        category_pills = soup.select('.category-pill')
        for pill in category_pills:
            if 'data-category' in pill.attrs:
                category = pill['data-category']
                if category != 'all':  # Skip the "All Reports" category
                    all_categories.append(category)
        
        # Extract all report cards
        for card in soup.select('.report-card'):
            # Extract report data
            title_elem = card.select_one('.report-title')
            desc_elem = card.select_one('.report-description')
            link_elem = card.select_one('.view-link')
            
            # Skip if any required element is missing
            if not title_elem or not desc_elem or not link_elem:
                continue
                
            # Get title, description, and filename
            title = html.unescape(title_elem.get_text().strip())
            description = html.unescape(desc_elem.get_text().strip())
            href = link_elem.get('href', '')
            filename = os.path.basename(href) if href else None
            
            # Skip if filename is missing
            if not filename:
                continue
                
            # Get categories
            categories = []
            if 'data-categories' in card.attrs:
                categories = card['data-categories'].split()
            
            # Check if the report is disabled
            enabled = not ('data-disabled' in card.attrs and card['data-disabled'] == 'true')
            
            # Store report data
            existing_reports[filename] = {
                'title': title,
                'description': description,
                'categories': categories,
                'enabled': enabled
            }
            
            # Track the order
            report_order.append(filename)
        
        # Add order information to the return value
        return {
            'reports': existing_reports,
            'order': report_order,
            'categories': all_categories
        }
        
    except Exception as e:
        print(f"Error extracting existing reports: {e}")
        return {'reports': {}, 'order': [], 'categories': []}

def update_showcase(showcase_file, reports_dir, refresh_existing=False):
    """
    Update the showcase HTML file with new report cards while preserving
    existing categorization, order, and settings.
    
    Args:
        showcase_file: Path to the showcase HTML file
        reports_dir: Path to the directory containing report HTML files
        refresh_existing: If True, refresh data for existing reports from their HTML files
    """
    if not os.path.exists(showcase_file):
        print(f"Showcase file {showcase_file} not found.")
        return
        
    if not os.path.exists(reports_dir):
        print(f"Reports directory {reports_dir} not found.")
        return
    
    # Create a real timestamped backup of the showcase file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{showcase_file.replace('.html', '')}_{timestamp}_backup.html"
    try:
        shutil.copy2(showcase_file, backup_path)
        print(f"Created backup of showcase file: {backup_path}")
    except Exception as e:
        print(f"Warning: Failed to create backup: {e}")
        # Continue anyway - we might be creating a new file
    
    # Extract existing data from the showcase file
    existing_data = extract_existing_reports_data(showcase_file)
    existing_reports = existing_data.get('reports', {})
    existing_order = existing_data.get('order', [])
    all_categories = existing_data.get('categories', [])
    
    print(f"Found {len(existing_reports)} existing reports with {len(all_categories)} categories")
    
    # Get all HTML files in the reports directory
    html_files = [f for f in os.listdir(reports_dir) if f.endswith('.html') and not f.startswith('.')]
    
    # Track new reports and updated reports
    new_reports = []
    updated_reports = []
    
    # Process each HTML file
    for filename in html_files:
        file_path = os.path.join(reports_dir, filename)
        
        # Check if this report already exists in the showcase
        if filename in existing_reports and not refresh_existing:
            # Report exists, reuse existing data
            print(f"Preserving existing data for {filename}")
            continue
        elif filename in existing_reports and refresh_existing:
            # Report exists, but we're refreshing all data
            print(f"Refreshing data for existing report: {filename}")
            title, categories = extract_title_and_categories(file_path)
            description = extract_first_paragraph(file_path)
            
            # Preserve the enabled/disabled state
            enabled = existing_reports[filename].get('enabled', True)
            
            # Update the report data
            existing_reports[filename] = {
                'title': title,
                'description': description,
                'categories': categories,
                'enabled': enabled  # Preserve enabled state
            }
            
            # Add any new categories to the list
            for category in categories:
                if category not in all_categories:
                    all_categories.append(category)
            
            updated_reports.append(filename)
        else:
            # This is a new report, process it
            print(f"Processing new report: {filename}")
            title, categories = extract_title_and_categories(file_path)
            description = extract_first_paragraph(file_path)
            
            # Store new report data
            existing_reports[filename] = {
                'title': title,
                'description': description,
                'categories': categories,
                'enabled': True  # Enable by default
            }
            
            # Add any new categories to the list
            for category in categories:
                if category not in all_categories:
                    all_categories.append(category)
            
            new_reports.append(filename)
    
    # Update the order to include new reports at the end
    updated_order = existing_order.copy()
    for filename in new_reports:
        if filename not in updated_order:
            updated_order.append(filename)
    
    # Ensure all reports are in the order list
    for filename in existing_reports:
        if filename not in updated_order:
            updated_order.append(filename)
    
    # If we have a showcase file, use its structure as a base
    if os.path.exists(showcase_file):
        with open(showcase_file, 'r', encoding='utf-8') as file:
            showcase_content = file.read()
        soup = BeautifulSoup(showcase_content, 'html.parser')
    else:
        # Create a basic structure if no file exists
        soup = BeautifulSoup('''
        <html>
        <head>
            <title>Instructor Reports Showcase</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">
            <style>
                /* Basic styling will be added here */
                body { font-family: Arial, sans-serif; margin: 0; padding: 0; }
                .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
                .category-bar { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 20px; }
                .category-pill { background: #f0f0f0; border: none; padding: 8px 16px; border-radius: 20px; cursor: pointer; }
                .category-pill.active { background: #007bff; color: white; }
                .report-cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
                .report-card { border: 1px solid #ddd; border-radius: 8px; padding: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
                .report-title { font-size: 18px; font-weight: bold; margin-bottom: 10px; }
                .report-description { font-size: 14px; color: #666; margin-bottom: 15px; }
                .view-link { display: inline-block; color: #007bff; text-decoration: none; font-size: 14px; }
                /* Dark mode */
                body.dark-mode { background-color: #222; color: #eee; }
                body.dark-mode .report-card { background-color: #333; border-color: #444; }
                body.dark-mode .report-description { color: #bbb; }
                body.dark-mode .category-pill { background: #444; color: #eee; }
                body.dark-mode .category-pill.active { background: #0066cc; }
                .theme-toggle { position: fixed; top: 20px; right: 20px; background: none; border: none; color: inherit; font-size: 24px; cursor: pointer; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Instructor Reports Showcase</h1>
                <div class="category-bar">
                    <button class="category-pill active" data-category="all">All Reports</button>
                </div>
                <div class="report-cards">
                    <!-- Report cards will be inserted here -->
                </div>
            </div>
            <button class="theme-toggle" id="theme-toggle" aria-label="Toggle Dark Mode">
                <i class="fas fa-moon"></i>
            </button>
            <script>
                // Category filtering
                document.querySelectorAll('.category-pill').forEach(pill => {
                    pill.addEventListener('click', () => {
                        // Update active state
                        document.querySelectorAll('.category-pill').forEach(p => p.classList.remove('active'));
                        pill.classList.add('active');
                        
                        const category = pill.getAttribute('data-category');
                        
                        // Filter cards
                        document.querySelectorAll('.report-card').forEach(card => {
                            if (category === 'all' || card.getAttribute('data-categories').includes(category)) {
                                card.style.display = '';
                            } else {
                                card.style.display = 'none';
                            }
                        });
                    });
                });
                
                // Theme toggle
                const themeToggle = document.getElementById('theme-toggle');
                const body = document.body;
                const icon = themeToggle.querySelector('i');
                
                // Check for saved theme preference
                const savedTheme = localStorage.getItem('theme');
                if (savedTheme === 'dark') {
                    body.classList.add('dark-mode');
                    icon.classList.remove('fa-moon');
                    icon.classList.add('fa-sun');
                }
                
                themeToggle.addEventListener('click', () => {
                    body.classList.toggle('dark-mode');
                    
                    if (body.classList.contains('dark-mode')) {
                        icon.classList.remove('fa-moon');
                        icon.classList.add('fa-sun');
                        localStorage.setItem('theme', 'dark');
                    } else {
                        icon.classList.remove('fa-sun');
                        icon.classList.add('fa-moon');
                        localStorage.setItem('theme', 'light');
                    }
                });
                
                // Don't show disabled reports
                document.querySelectorAll('.report-card[data-disabled="true"]').forEach(card => {
                    card.style.display = 'none';
                });
            </script>
        </body>
        </html>
        ''', 'html.parser')
    
    # Update category pills - preserve existing categories
    category_bar = soup.select_one('.category-bar')
    if category_bar:
        category_bar.clear()
        
        # Add "All Reports" pill
        all_pill = soup.new_tag('button')
        all_pill['class'] = 'category-pill active'
        all_pill['data-category'] = 'all'
        all_pill.string = 'All Reports'
        category_bar.append(all_pill)
        
        # Add all other category pills
        for category in all_categories:
            pill = soup.new_tag('button')
            pill['class'] = 'category-pill'
            pill['data-category'] = category
            pill.string = category.replace('-', ' ').title()
            category_bar.append(pill)
    
    # Update report cards container
    report_cards_container = soup.select_one('.report-cards')
    if report_cards_container:
        report_cards_container.clear()
        
        # Add cards in the specified order
        for filename in updated_order:
            if filename in existing_reports:
                report_data = existing_reports[filename]
                
                # Create a new report card
                card = soup.new_tag('div')
                card['class'] = 'report-card'
                
                # Ensure categories are normalized (lowercase, no extra spaces)
                normalized_categories = [c.strip().lower() for c in report_data['categories']]
                # Remove any empty categories
                normalized_categories = [c for c in normalized_categories if c]
                
                # Set the data-categories attribute - this is critical for filtering
                card['data-categories'] = ' '.join(normalized_categories)
                
                # Add disabled attribute if report is disabled
                if not report_data.get('enabled', True):
                    card['data-disabled'] = 'true'
                    card['style'] = 'display: none;'  # Initially hidden
                
                # Add title - use a direct HTML approach to avoid escaping issues
                title_div = soup.new_tag('div')
                title_div['class'] = 'report-title'
                title_div.clear()
                
                # Insert as raw HTML instead of text to preserve entities
                title_html = BeautifulSoup(f"<span>{report_data['title']}</span>", 'html.parser')
                title_div.append(title_html.span.contents[0])
                card.append(title_div)
                
                # Add description - same approach
                desc_div = soup.new_tag('div')
                desc_div['class'] = 'report-description'
                desc_div.clear()
                
                # Insert as raw HTML instead of text to preserve entities
                desc_html = BeautifulSoup(f"<span>{report_data['description']}</span>", 'html.parser')
                desc_div.append(desc_html.span.contents[0])
                card.append(desc_div)
                
                # Add link
                link = soup.new_tag('a')
                link['class'] = 'view-link'
                link['href'] = f"instructor_reports/{filename}"
                link['target'] = '_blank'
                
                # Add icon to link
                icon = soup.new_tag('i')
                icon['class'] = ['fas', 'fa-external-link-alt', 'mr-1']
                link.append(icon)
                
                # Add text to link
                link.append(" View Full Report")
                
                card.append(link)
                
                # Add the report card to the container
                report_cards_container.append(card)
    
    # Save the updated showcase file
    html_output = str(soup)
    with open(showcase_file, 'w', encoding='utf-8') as file:
        file.write(html_output)
    
    # Also save a JSON backup of all report data for safer recovery
    json_backup = f"{showcase_file.replace('.html', '')}_{timestamp}_data.json"
    with open(json_backup, 'w', encoding='utf-8') as f:
        json.dump({
            'reports': existing_reports,
            'order': updated_order,
            'categories': all_categories
        }, f, indent=2)
    
    print(f"Updated showcase with {len(html_files)} reports ({len(new_reports)} new, {len(updated_reports)} refreshed)")
    print(f"JSON backup of all report data saved to: {json_backup}")
    
    return {
        'reports': existing_reports,
        'new_reports': new_reports,
        'updated_reports': updated_reports,
        'categories': all_categories,
        'order': updated_order
    }

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Update the instructor reports showcase.')
    parser.add_argument('--refresh-existing', action='store_true',
                       help='Refresh data for existing reports from their HTML files')
    parser.add_argument('--showcase-file', type=str,
                       default="/Users/simon/Documents/GitHub/SwayReports/instructor_reports_showcase.html",
                       help='Path to the showcase HTML file')
    parser.add_argument('--reports-dir', type=str,
                       default="/Users/simon/Documents/GitHub/SwayReports/instructor_reports",
                       help='Path to the directory containing instructor reports')
    
    args = parser.parse_args()
    
    # Run the update with the specified options
    result = update_showcase(args.showcase_file, args.reports_dir, args.refresh_existing)
    
    # Show a summary
    if args.refresh_existing and result['updated_reports']:
        print("\nRefreshed reports from HTML source:")
        for filename in result['updated_reports']:
            print(f"- {filename}")
    
    if result['new_reports']:
        print("\nNew reports added:")
        for filename in result['new_reports']:
            print(f"- {filename}")
    
    print(f"\nTotal reports: {len(result['reports'])}")
    print(f"Categories: {', '.join(result['categories'])}")
    print("\nYour showcase has been updated. All your manual work is preserved.")
    if not args.refresh_existing:
        print("\nNote: Use --refresh-existing if you want to update titles/descriptions from HTML files.") 