#!/usr/bin/env python3
import os
import json
import sys
import glob
from bs4 import BeautifulSoup
from update_showcase import update_showcase, extract_existing_reports_data

def list_backup_files():
    """List all available showcase backup files."""
    backup_files = []
    
    # Find HTML backups
    html_backups = glob.glob("instructor_reports_showcase_*_backup.html")
    backup_files.extend(html_backups)
    
    # Find JSON backups
    json_backups = glob.glob("instructor_reports_showcase_*_data.json")
    backup_files.extend(json_backups)
    
    # Sort by timestamp (most recent first)
    backup_files.sort(reverse=True)
    
    return backup_files

def recover_from_html_backup(backup_file, output_file):
    """Recover categories and report data from an HTML backup file."""
    # Extract data from backup file
    print(f"Extracting data from {backup_file}...")
    backup_data = extract_existing_reports_data(backup_file)
    
    # Save to main showcase file, preserving the data but updating reports
    print(f"Recovering data to {output_file}...")
    
    # We'll use our modified update_showcase function, which now preserves existing data
    # but we need to first put the backup data in place of the main file
    if os.path.exists(output_file):
        # Rename current file as a secondary backup
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        pre_recovery_backup = f"{output_file.replace('.html', '')}_{timestamp}_pre_recovery.html"
        os.rename(output_file, pre_recovery_backup)
        print(f"Created backup of current file: {pre_recovery_backup}")
    
    # Copy backup file to main file location
    import shutil
    shutil.copy2(backup_file, output_file)
    print(f"Restored {backup_file} to {output_file}")
    
    # Now run update_showcase to process any new reports while preserving our restored data
    update_showcase(output_file, "instructor_reports")
    
    print("Recovery successful! Your category assignments and report order have been restored.")

def recover_from_json_backup(json_file, output_file):
    """Recover categories and report data from a JSON backup file."""
    try:
        # Load the JSON data
        print(f"Loading data from {json_file}...")
        with open(json_file, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
            
        # Verify JSON data structure
        if not all(key in backup_data for key in ['reports', 'order', 'categories']):
            print("Error: Invalid JSON backup format. Missing required data.")
            return False
        
        # Get the current showcase file data
        if os.path.exists(output_file):
            # Read the current file to keep its structure
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse with BeautifulSoup 
            soup = BeautifulSoup(content, 'html.parser')
            
            # Create a backup of the current file
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            pre_recovery_backup = f"{output_file.replace('.html', '')}_{timestamp}_pre_recovery.html"
            with open(pre_recovery_backup, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Created backup of current file: {pre_recovery_backup}")
        else:
            # Create a new file with a default structure
            print("Main showcase file not found. Creating a new one...")
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
        
        # Write the recovered file with JSON data integrated
        with open(output_file, 'w', encoding='utf-8') as f:
            # Update categories
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
                for category in backup_data['categories']:
                    pill = soup.new_tag('button')
                    pill['class'] = 'category-pill'
                    pill['data-category'] = category
                    pill.string = category.replace('-', ' ').title()
                    category_bar.append(pill)
            
            # Write initial structure 
            f.write(str(soup))
        
        # Now update the showcase with our recovered data
        # The update_showcase function will preserve the categories and use the existing reports data
        update_showcase(output_file, "instructor_reports")
        
        print("Recovery successful! Your category assignments and report order have been restored.")
        return True
        
    except Exception as e:
        print(f"Error recovering from JSON file: {e}")
        return False

def main():
    output_file = "instructor_reports_showcase.html"
    
    if len(sys.argv) > 1:
        # User provided a specific backup file
        backup_file = sys.argv[1]
        if not os.path.exists(backup_file):
            print(f"Error: Backup file '{backup_file}' not found.")
            return
    else:
        # List available backup files
        backup_files = list_backup_files()
        
        if not backup_files:
            print("No backup files found. Make sure you're in the right directory.")
            return
        
        print("Available backup files:")
        for i, file in enumerate(backup_files):
            print(f"{i+1}. {file}")
        
        # Ask user to choose a file
        choice = input("Enter the number of the backup file to recover from (or 'q' to quit): ")
        if choice.lower() == 'q':
            return
        
        try:
            index = int(choice) - 1
            if 0 <= index < len(backup_files):
                backup_file = backup_files[index]
            else:
                print("Invalid selection.")
                return
        except ValueError:
            print("Invalid input. Please enter a number.")
            return
    
    # Perform recovery based on file type
    if backup_file.endswith('.html'):
        recover_from_html_backup(backup_file, output_file)
    elif backup_file.endswith('.json'):
        recover_from_json_backup(backup_file, output_file)
    else:
        print(f"Unsupported backup file format: {backup_file}")

if __name__ == "__main__":
    main() 