#!/usr/bin/env python3
from bs4 import BeautifulSoup, NavigableString
import html

def test_bs4_escaping():
    print("==== Testing BeautifulSoup HTML entity handling ====")
    
    # Original text with an ampersand
    text_with_ampersand = "Test & Ampersand"
    
    # Create a sample HTML document
    soup = BeautifulSoup('<div id="container"></div>', 'html.parser')
    container = soup.find(id="container")
    
    # Method 1: Using .string
    print("\nMethod 1: Using .string")
    test_div1 = soup.new_tag('div')
    test_div1.string = text_with_ampersand
    print(f"Output: {test_div1}")
    
    # Method 2: Using .append
    print("\nMethod 2: Using .append")
    test_div2 = soup.new_tag('div')
    test_div2.append(text_with_ampersand)
    print(f"Output: {test_div2}")
    
    # Method 3: Using NavigableString
    print("\nMethod 3: Using NavigableString")
    test_div3 = soup.new_tag('div')
    test_div3.append(NavigableString(text_with_ampersand))
    print(f"Output: {test_div3}")
    
    # Method 4: Using NavigableString with html.unescape
    print("\nMethod 4: Using NavigableString with html.unescape")
    test_div4 = soup.new_tag('div')
    test_div4.append(NavigableString(html.unescape(text_with_ampersand)))
    print(f"Output: {test_div4}")
    
    # Method 5: Directly constructing HTML
    print("\nMethod 5: Constructing HTML and then parsing")
    raw_html = f'<div>{text_with_ampersand}</div>'
    parsed = BeautifulSoup(raw_html, 'html.parser')
    test_div5 = parsed.div
    print(f"Output: {test_div5}")
    
    # Method 6: Append new soup
    print("\nMethod 6: Using append with a new soup")
    test_div6 = soup.new_tag('div')
    new_soup = BeautifulSoup(text_with_ampersand, 'html.parser')
    test_div6.append(new_soup)
    print(f"Output: {test_div6}")
    
    # Full document test
    print("\n==== Testing with full document ====")
    doc = BeautifulSoup('''
    <html>
      <body>
        <div class="report-cards"></div>
      </body>
    </html>
    ''', 'html.parser')
    
    card_container = doc.select_one('.report-cards')
    
    # Create a report card the right way
    card = doc.new_tag('div')
    card['class'] = 'report-card'
    
    # Create methods that work
    title_div = doc.new_tag('div')
    title_div['class'] = 'report-title'
    
    # Use the best method based on tests above
    title_content = BeautifulSoup(text_with_ampersand, 'html.parser')
    title_div.append(title_content)
    
    card.append(title_div)
    card_container.append(card)
    
    print(f"Final document with correct method:\n{doc}")

if __name__ == "__main__":
    test_bs4_escaping() 