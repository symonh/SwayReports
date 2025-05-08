#!/usr/bin/env python3
import os
import re
import random
from pathlib import Path
from bs4 import BeautifulSoup

def extract_title_and_categories(html_file):
    """
    Extract the title and infer categories based on the filename and content.
    
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
                
                # Process the text to limit to 60 words + remainder of sentence
                words = text.split()
                
                if len(words) <= 50:
                    # If the paragraph is less than 60 words, return it all
                    return text
                
                # Get the first 50 words
                truncated_text = ' '.join(words[:50])
                
                # Find the end of the current sentence after 60 words
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

def update_showcase(showcase_file, reports_dir):
    """
    Update the showcase HTML file with new report cards.
    
    Args:
        showcase_file: Path to the showcase HTML file
        reports_dir: Path to the directory containing report HTML files
    """
    if not os.path.exists(showcase_file):
        print(f"Showcase file {showcase_file} not found.")
        return
        
    if not os.path.exists(reports_dir):
        print(f"Reports directory {reports_dir} not found.")
        return
    
    # Create a backup of the showcase file
    backup_path = showcase_file.replace('.html', '_backup.html')
    with open(showcase_file, 'r', encoding='utf-8') as file:
        showcase_content = file.read()
    
    with open(backup_path, 'w', encoding='utf-8') as file:
        file.write(showcase_content)
    
    print(f"Created backup of showcase file: {backup_path}")
    
    # Parse the showcase HTML
    soup = BeautifulSoup(showcase_content, 'html.parser')
    
    # Find the container for report cards
    report_cards_container = soup.select_one('.report-cards')
    
    if not report_cards_container:
        print("Could not find .report-cards container in the showcase file.")
        return
    
    # Clear all existing report cards
    report_cards_container.clear()
    
    # Get all HTML files in the reports directory
    html_files = [f for f in os.listdir(reports_dir) if f.endswith('.html') and not f.startswith('.')]
    
    # Process each HTML file
    for filename in html_files:
        file_path = os.path.join(reports_dir, filename)
        
        # Extract title and categories
        title, categories = extract_title_and_categories(file_path)
        
        # Extract the first paragraph
        description = extract_first_paragraph(file_path)
        
        # Create a new report card
        report_card = soup.new_tag('div')
        report_card['class'] = 'report-card'
        report_card['data-categories'] = " ".join(categories)
        
        # Add title
        title_div = soup.new_tag('div')
        title_div['class'] = 'report-title'
        title_div.string = title
        report_card.append(title_div)
        
        # Add description
        desc_div = soup.new_tag('div')
        desc_div['class'] = 'report-description'
        desc_div.string = description
        report_card.append(desc_div)
        
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
        
        report_card.append(link)
        
        # Add the report card to the container
        report_cards_container.append(report_card)
    
    # Save the updated showcase file
    with open(showcase_file, 'w', encoding='utf-8') as file:
        file.write(str(soup))
    
    print(f"Updated showcase with {len(html_files)} report cards.")

if __name__ == "__main__":
    showcase_file = "/Users/simon/Documents/GitHub/SwayReports/instructor_reports_showcase.html"
    reports_dir = "/Users/simon/Documents/GitHub/SwayReports/instructor_reports"
    update_showcase(showcase_file, reports_dir) 