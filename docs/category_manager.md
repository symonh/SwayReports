# Sway Reports Category Manager

A simple Flask web application for managing categories in the Instructor Reports Showcase.

## Features

- Add, rename, and delete categories
- Assign categories to instructor reports
- Search through reports for easier management
- Real-time category assignment with a user-friendly interface
- Statistics showing category usage
- **NEW: Drag and drop reordering** of reports to control their display order in the showcase

## Setup and Installation

1. Make sure Python 3.6+ is installed
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the Category Manager:
   ```
   python category_manager.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

3. Use the interface to:
   - Add new categories in the left panel
   - Rename existing categories
   - Delete categories (this will remove the category from all reports)
   - View category usage statistics
   - Search for specific reports using the search box
   - Assign categories to reports by selecting from the dropdown and clicking Save

4. After making changes, you can view the updated showcase by clicking the "View Showcase" button or by opening `instructor_reports_showcase.html` directly.

### Managing Report Order

You can now control the exact order in which reports appear in the showcase:

1. Look for the grip lines (≡) handle on the right side of each report card
2. Click and drag the handle to move a report to a new position
3. The new order is automatically saved when you release the mouse button
4. The showcase will immediately reflect the new order

This feature makes it easy to:
- Put your most important reports at the top
- Group related reports together
- Create a logical flow through your showcase

## Implementation Details

The Category Manager uses:
- Flask for the web application framework
- Beautiful Soup to parse and modify the HTML showcase file
- Bootstrap for styling the interface

Changes are applied directly to the `instructor_reports_showcase.html` file, so it's recommended to make a backup before using the manager extensively.

## Tips

- Category names are automatically converted to lowercase and spaces are replaced with hyphens
- When renaming a category, it will be updated for all reports that use it
- You can select multiple categories for a report by holding Ctrl (or Cmd on Mac) while clicking
- Search functionality helps you quickly find reports for category assignment 