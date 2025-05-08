#!/usr/bin/env python3
import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from bs4 import BeautifulSoup
import json
import html
from pathlib import Path

app = Flask(__name__)

# Configuration
SHOWCASE_FILE = "instructor_reports_showcase.html"
REPORTS_DIR = "instructor_reports"

def parse_showcase_file():
    """Parse the showcase HTML file and extract categories and reports"""
    with open(SHOWCASE_FILE, 'r', encoding='utf-8') as file:
        content = file.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    
    # Extract categories
    categories = []
    category_pills = soup.select('.category-pill')
    for pill in category_pills:
        if 'data-category' in pill.attrs:
            category = pill['data-category']
            if category != 'all':  # Skip the "All Reports" category
                categories.append(category)
    
    # Extract reports and their assigned categories
    reports = []
    report_cards = soup.select('.report-card')
    for idx, card in enumerate(report_cards):
        # Use get_text() to get the raw text and html.unescape to properly handle entities
        title = html.unescape(card.select_one('.report-title').get_text().strip())
        description = html.unescape(card.select_one('.report-description').get_text().strip())
        link = card.select_one('.view-link')['href']
        filename = os.path.basename(link)
        
        # Get assigned categories
        assigned_categories = []
        if 'data-categories' in card.attrs:
            assigned_categories = card['data-categories'].split()
        
        # Check if report is disabled (hidden)
        enabled = not ('data-disabled' in card.attrs and card['data-disabled'] == 'true')
        
        reports.append({
            'title': title,
            'description': description,
            'filename': filename,
            'categories': assigned_categories,
            'enabled': enabled,
            'position': idx + 1  # Add position information (1-based)
        })
    
    return categories, reports

def save_showcase_file(categories, reports):
    """Save updated categories and report assignments back to the showcase file"""
    with open(SHOWCASE_FILE, 'r', encoding='utf-8') as file:
        content = file.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    
    # Update category pills
    category_bar = soup.select_one('.category-bar')
    category_bar.clear()
    
    # Add "All Reports" pill
    all_pill = soup.new_tag('button')
    all_pill['class'] = 'category-pill active'
    all_pill['data-category'] = 'all'
    all_pill.string = 'All Reports'
    category_bar.append(all_pill)
    
    # Add all other category pills
    for category in categories:
        pill = soup.new_tag('button')
        pill['class'] = 'category-pill'
        pill['data-category'] = category
        pill.string = category.replace('-', ' ').title()
        category_bar.append(pill)
    
    # Sort reports by position if specified
    if any('position' in report for report in reports):
        reports.sort(key=lambda r: r.get('position', float('inf')))
    
    # Update report cards
    report_cards_container = soup.select_one('.report-cards')
    report_cards_container.clear()
    
    # Make sure we completely clear any existing report cards
    # by removing all children elements
    while report_cards_container.contents:
        report_cards_container.contents[0].decompose()
    
    # Create cards in the specified order
    for report in reports:
        # Create a new report card
        card = soup.new_tag('div')
        card['class'] = 'report-card'
        
        # Ensure categories are normalized and non-empty
        valid_categories = [c.strip().lower() for c in report['categories'] if c.strip()]
        card['data-categories'] = ' '.join(valid_categories)
        
        # Always set the disabled attribute explicitly to ensure frontend JS works correctly
        card['data-disabled'] = str(not report.get('enabled', True)).lower()
        if not report.get('enabled', True):
            card['class'] = 'report-card disabled-report'
            card['style'] = 'display: none;'  # Initially hidden
        
        # Create title div - use a direct HTML approach to avoid escaping issues
        title_div = soup.new_tag('div')
        title_div['class'] = 'report-title'
        title_div.clear()
        # Insert as raw HTML instead of text to preserve entities
        title_html = BeautifulSoup(f"<span>{report['title']}</span>", 'html.parser')
        title_div.append(title_html.span.contents[0])
        card.append(title_div)
        
        # Create description div - same approach
        desc_div = soup.new_tag('div')
        desc_div['class'] = 'report-description'
        desc_div.clear()
        # Insert as raw HTML instead of text to preserve entities
        desc_html = BeautifulSoup(f"<span>{report['description']}</span>", 'html.parser')
        desc_div.append(desc_html.span.contents[0])
        card.append(desc_div)
        
        # Create link
        link = soup.new_tag('a')
        link['class'] = 'view-link'
        link['href'] = f"instructor_reports/{report['filename']}"
        link['target'] = '_blank'
        
        # Create icon for link
        icon = soup.new_tag('i')
        icon['class'] = 'fas fa-external-link-alt mr-1'
        link.append(icon)
        
        link.append(' View Full Report')
        card.append(link)
        
        report_cards_container.append(card)
    
    # Update the JavaScript to dynamically update category counts
    script_tag = soup.find('script', string=lambda s: s and 'category filtering' in s.lower())
    if not script_tag:
        script_tag = soup.new_tag('script')
        if soup.body:
            soup.body.append(script_tag)
    
    # Replace or add our enhanced script for dynamic category counts
    script_tag.string = '''
    // Function to update category counts
    function updateCategoryCounts() {
        const categories = {};
        const allReportsCount = document.querySelectorAll('.report-card:not([data-disabled="true"])').length;
        
        // Reset counts
        document.querySelectorAll('.category-pill').forEach(pill => {
            const category = pill.getAttribute('data-category');
            if (category === 'all') {
                pill.textContent = `All Reports (${allReportsCount})`;
            } else {
                categories[category] = 0;
            }
        });
        
        // Count reports for each category
        document.querySelectorAll('.report-card:not([data-disabled="true"])').forEach(card => {
            const cardCategories = (card.getAttribute('data-categories') || '').split(' ');
            cardCategories.forEach(category => {
                if (category && categories.hasOwnProperty(category)) {
                    categories[category]++;
                }
            });
        });
        
        // Update category pills with counts
        for (const [category, count] of Object.entries(categories)) {
            const pill = document.querySelector(`.category-pill[data-category="${category}"]`);
            if (pill) {
                const name = category.replace(/-/g, ' ').replace(/\\b\\w/g, c => c.toUpperCase());
                pill.textContent = `${name} (${count})`;
            }
        }
    }
    
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
    
    // Update category counts on page load
    document.addEventListener('DOMContentLoaded', updateCategoryCounts);
    
    // Theme toggle
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
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
    }
    
    // Don't show disabled reports
    document.querySelectorAll('.report-card[data-disabled="true"]').forEach(card => {
        card.style.display = 'none';
    });
    '''
    
    # Save the updated showcase file with HTML preserved
    html_output = str(soup)
    with open(SHOWCASE_FILE, 'w', encoding='utf-8') as file:
        file.write(html_output)

def update_report_title(report_filename, new_title):
    """Update the <title> and main heading in the instructor report HTML file."""
    report_path = Path(REPORTS_DIR) / report_filename
    if not report_path.exists():
        return False
    with open(report_path, 'r', encoding='utf-8') as f:
        content = f.read()
    soup = BeautifulSoup(content, 'html.parser')
    # Update <title>
    if soup.title:
        soup.title.clear()
        title_html = BeautifulSoup(f"<span>{new_title}</span>", 'html.parser')
        soup.title.append(title_html.span.contents[0])
    # Update main heading (try h1 first, fallback to first h1 or h2)
    h1 = soup.find('h1')
    if h1:
        h1.clear()
        h1_html = BeautifulSoup(f"<span>{new_title}</span>", 'html.parser')
        h1.append(h1_html.span.contents[0])
    else:
        h2 = soup.find('h2')
        if h2:
            h2.clear()
            h2_html = BeautifulSoup(f"<span>{new_title}</span>", 'html.parser')
            h2.append(h2_html.span.contents[0])
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    return True

@app.route('/')
def index():
    """Main page for category management"""
    categories, reports = parse_showcase_file()
    
    # Sort reports by position if available, otherwise by title
    if any('position' in report for report in reports):
        reports.sort(key=lambda r: r.get('position', float('inf')))
    else:
        reports.sort(key=lambda r: r['title'])
    
    # Calculate category counts for sidebar display
    category_counts = {'all': len([r for r in reports if r.get('enabled', True)])}
    for category in categories:
        category_counts[category] = len([r for r in reports if category in r['categories'] and r.get('enabled', True)])
    
    return render_template('category_manager.html', categories=categories, reports=reports, category_counts=category_counts)

@app.route('/categories', methods=['GET', 'POST'])
def manage_categories():
    """Handle category management"""
    categories, reports = parse_showcase_file()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            new_category = request.form.get('new_category').lower().strip().replace(' ', '-')
            if new_category and new_category not in categories:
                categories.append(new_category)
        
        elif action == 'delete':
            category_to_delete = request.form.get('category')
            if category_to_delete in categories:
                categories.remove(category_to_delete)
                
                # Also remove this category from all reports
                for report in reports:
                    if category_to_delete in report['categories']:
                        report['categories'].remove(category_to_delete)
        
        elif action == 'rename':
            old_category = request.form.get('old_category')
            new_category = request.form.get('new_category').lower().strip().replace(' ', '-')
            
            if old_category in categories and new_category and new_category not in categories:
                # Replace the category in the list
                index = categories.index(old_category)
                categories[index] = new_category
                
                # Update all reports using this category
                for report in reports:
                    if old_category in report['categories']:
                        report['categories'].remove(old_category)
                        report['categories'].append(new_category)
        
        # Save changes
        save_showcase_file(categories, reports)
        
        # Force update the showcase file to reflect the category changes
        showcase_path = os.path.abspath(SHOWCASE_FILE)
        reports_dir = os.path.abspath(REPORTS_DIR)
        
        try:
            # Import and reload update_showcase module
            import sys
            import importlib
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            import update_showcase
            importlib.reload(update_showcase)
            
            # Update the showcase with the new categories
            update_showcase.update_showcase(showcase_path, reports_dir, refresh_existing=False)
            print("Automatically updated showcase after category change")
        except Exception as e:
            print(f"Error updating showcase after category change: {e}")
        
        return redirect(url_for('index'))
    
    return render_template('category_manager.html', categories=categories, reports=reports)

@app.route('/assign', methods=['POST'])
def assign_categories():
    """Handle category assignment to reports"""
    categories, reports = parse_showcase_file()
    
    report_index = int(request.form.get('report_index'))
    new_categories = request.form.getlist('categories')
    new_title = request.form.get('report_title')
    
    if 0 <= report_index < len(reports):
        reports[report_index]['categories'] = new_categories
        
        # Update title if changed
        if new_title and new_title != reports[report_index]['title']:
            reports[report_index]['title'] = new_title
            # Also update the actual report file
            update_report_title(reports[report_index]['filename'], new_title)
            
        save_showcase_file(categories, reports)
    
    return redirect(url_for('index'))

@app.route('/update_position', methods=['POST'])
def update_position():
    """Update the position of a report in the showcase"""
    categories, reports = parse_showcase_file()
    
    report_index = int(request.form.get('report_index'))
    new_position = int(request.form.get('new_position'))
    
    if 0 <= report_index < len(reports) and 1 <= new_position <= len(reports):
        # Get the report to move
        report_to_move = reports[report_index]
        
        # Remove the report from its current position
        reports.pop(report_index)
        
        # Get the zero-based position (since new_position is 1-based)
        zero_based_position = new_position - 1
        
        # Insert the report at the new position
        reports.insert(zero_based_position, report_to_move)
        
        # Update all positions
        for i, report in enumerate(reports):
            report['position'] = i + 1
        
        # Save the updated showcase
        save_showcase_file(categories, reports)
        
        return redirect(url_for('index'))
    
    return jsonify({"success": False, "error": "Invalid report index or position"}), 400

@app.route('/api/reports', methods=['GET'])
def get_reports():
    """API endpoint to get reports data"""
    categories, reports = parse_showcase_file()
    return jsonify(reports)

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """API endpoint to get categories data"""
    categories, reports = parse_showcase_file()
    return jsonify(categories)

@app.route('/api/assign', methods=['POST'])
def api_assign_categories():
    """API endpoint to assign categories to a report"""
    data = request.json
    report_filename = data.get('filename')
    new_categories = data.get('categories', [])
    
    categories, reports = parse_showcase_file()
    
    for report in reports:
        if report['filename'] == report_filename:
            report['categories'] = new_categories
            save_showcase_file(categories, reports)
            return jsonify({"success": True})
    
    return jsonify({"success": False, "error": "Report not found"})

@app.route('/api/update_title', methods=['POST'])
def api_update_title():
    """API endpoint to update a report title"""
    data = request.json
    filename = data.get('filename')
    new_title = data.get('title')
    if not filename or not new_title:
        return jsonify({'success': False, 'error': 'Missing filename or title'}), 400
    # Update the instructor report HTML file
    ok = update_report_title(filename, new_title)
    if not ok:
        return jsonify({'success': False, 'error': 'Report file not found'}), 404
    # Update the showcase file
    categories, reports = parse_showcase_file()
    for report in reports:
        if report['filename'] == filename:
            report['title'] = new_title
            save_showcase_file(categories, reports)
            break
    return jsonify({'success': True})

@app.route('/api/reorder', methods=['POST'])
def api_reorder_reports():
    """API endpoint to reorder reports in the showcase"""
    data = request.json
    report_order = data.get('report_order', [])
    
    if not report_order:
        return jsonify({'success': False, 'error': 'Missing report order'}), 400
    
    categories, reports = parse_showcase_file()
    
    # Create a lookup of filename -> report
    report_lookup = {report['filename']: report for report in reports}
    
    # Create a new ordered list of reports
    new_reports = []
    for idx, filename in enumerate(report_order):
        if filename in report_lookup:
            report = report_lookup[filename]
            report['position'] = idx + 1  # Update position
            new_reports.append(report)
    
    # Add any reports that weren't in the order list at the end
    for report in reports:
        if report['filename'] not in report_order:
            report['position'] = len(new_reports) + 1
            new_reports.append(report)
    
    # Save the reordered reports
    save_showcase_file(categories, new_reports)
    
    return jsonify({'success': True})

@app.route('/api/toggle_visibility', methods=['POST'])
def api_toggle_visibility():
    """API endpoint to toggle report visibility"""
    data = request.json
    filename = data.get('filename')
    enabled = data.get('enabled')
    
    if filename is None or enabled is None:
        return jsonify({'success': False, 'error': 'Missing filename or enabled state'}), 400
    
    categories, reports = parse_showcase_file()
    updated = False
    
    for report in reports:
        if report['filename'] == filename:
            report['enabled'] = enabled
            updated = True
            break
    
    if updated:
        save_showcase_file(categories, reports)
        
        # This is a critical update that should be immediately reflected in the showcase file
        # Force regenerate the showcase file with the updated visibility settings
        showcase_path = os.path.abspath(SHOWCASE_FILE)
        reports_dir = os.path.abspath(REPORTS_DIR)
        
        # Get the script to reimport/update module
        import importlib
        import sys
        
        # Import the update_showcase module (assuming it's in the same directory)
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        try:
            # Try to import the module
            import update_showcase
            
            # Reload if already imported
            importlib.reload(update_showcase)
            
            # Call the function to update the showcase
            update_showcase.update_showcase(showcase_path, reports_dir, refresh_existing=False)
            print(f"Automatically updated showcase after visibility change for report {filename} to enabled={enabled}")
        except Exception as e:
            print(f"Error updating showcase after visibility change: {e}")
        
        return jsonify({'success': True, 'enabled': enabled})
    else:
        return jsonify({'success': False, 'error': 'Report not found'}), 404

@app.route('/api/run_update_showcase', methods=['POST'])
def api_run_update_showcase():
    """API endpoint to run the update_showcase script"""
    try:
        # Get absolute paths
        showcase_path = os.path.abspath(SHOWCASE_FILE)
        reports_dir = os.path.abspath(REPORTS_DIR)
        
        # Get refresh_existing parameter from request data
        data = request.json or {}
        refresh_existing = data.get('refresh_existing', False)
        
        # Import the update_showcase module
        import sys
        import importlib
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import update_showcase
        importlib.reload(update_showcase)
        
        # Run the update_showcase function
        result = update_showcase.update_showcase(showcase_path, reports_dir, refresh_existing)
        
        # Return a message with the result
        return jsonify({
            'success': True,
            'message': f"Update completed successfully. Added {len(result.get('new_reports', []))} new reports, updated {len(result.get('updated_reports', []))} existing reports."
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Create templates directory and template file if they don't exist
os.makedirs('templates', exist_ok=True)

if __name__ == '__main__':
    app.run(debug=True, port=5001) 