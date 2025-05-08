#!/usr/bin/env python3
import os
from bs4 import BeautifulSoup
import html

def create_test_file(filename, content):
    """Create a test HTML file."""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created test file: {filename}")

def test_ampersand_handling():
    """Test different approaches for handling ampersands in BeautifulSoup."""
    # Create a simple test HTML file with an ampersand in the title
    test_file = "test_ampersand.html"
    create_test_file(test_file, """
    <html>
    <head>
        <title>Test & Sample</title>
    </head>
    <body>
        <h1 class="generated-title">Circumcision, Parental Leave & Other Topics</h1>
        <div id="report-content" class="markdown-content">
            <p>This is a paragraph with an ampersand & in it. Let's see how it works.</p>
        </div>
    </body>
    </html>
    """)
    
    # Create a showcase test file
    showcase_file = "test_showcase.html"
    create_test_file(showcase_file, """
    <html>
    <head>
        <title>Test Showcase</title>
    </head>
    <body>
        <div class="category-bar">
            <button class="category-pill active" data-category="all">All Reports</button>
        </div>
        <div class="report-cards">
        </div>
    </body>
    </html>
    """)
    
    # Test our solution from update_showcase.py
    print("\n=== Testing our solution ===")
    
    # First, extract title and description
    with open(test_file, 'r', encoding='utf-8') as file:
        content = file.read()
    
    title_match = re.search(r'<h1\s+class="generated-title">\s*(.*?)\s*</h1>', content, re.DOTALL)
    title = title_match.group(1).strip() if title_match else "Default Title"
    
    soup = BeautifulSoup(content, 'html.parser')
    report_content = soup.find('div', id='report-content')
    first_paragraph = report_content.find('p')
    description = first_paragraph.get_text().strip() if first_paragraph else "Default description"
    
    print(f"Extracted title: {title}")
    print(f"Extracted description: {description}")
    
    # Now update the showcase file using our solution
    with open(showcase_file, 'r', encoding='utf-8') as file:
        showcase_content = file.read()
    
    showcase_soup = BeautifulSoup(showcase_content, 'html.parser')
    report_cards = showcase_soup.select_one('.report-cards')
    
    # Create a report card with our solution
    card = showcase_soup.new_tag('div')
    card['class'] = 'report-card'
    
    # Add title using our solution
    title_div = showcase_soup.new_tag('div')
    title_div['class'] = 'report-title'
    title_div.clear()
    title_html = BeautifulSoup(f"<span>{title}</span>", 'html.parser')
    title_div.append(title_html.span.contents[0])
    card.append(title_div)
    
    # Add description using our solution
    desc_div = showcase_soup.new_tag('div')
    desc_div['class'] = 'report-description'
    desc_div.clear()
    desc_html = BeautifulSoup(f"<span>{description}</span>", 'html.parser')
    desc_div.append(desc_html.span.contents[0])
    card.append(desc_div)
    
    report_cards.append(card)
    
    # Save and examine the result
    output_file = "test_output.html"
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(str(showcase_soup))
    
    print(f"\nFinal HTML output saved to {output_file}")
    
    # Read it back and examine how ampersands are displayed
    with open(output_file, 'r', encoding='utf-8') as file:
        result = file.read()
    
    print("\nExamining how ampersands are stored in the HTML:")
    # Find and print the lines containing "ampersand"
    for line_num, line in enumerate(result.splitlines()):
        if 'ampersand' in line.lower() or '&' in line:
            print(f"Line {line_num+1}: {line}")
    
    # Clean up test files
    print("\nCleaning up test files...")
    for file in [test_file, showcase_file, output_file]:
        if os.path.exists(file):
            os.remove(file)
    
    print("Test completed.")

if __name__ == "__main__":
    import re
    test_ampersand_handling() 