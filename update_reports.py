#!/usr/bin/env python3
import os
import sys
import subprocess

def run_script(script_path):
    """
    Run a Python script and print its output.
    
    Args:
        script_path: Path to the Python script to run
    
    Returns:
        True if the script executed successfully, False otherwise
    """
    try:
        print(f"\n=== Running {os.path.basename(script_path)} ===\n")
        
        # Run the script and capture output
        result = subprocess.run([sys.executable, script_path], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE,
                              text=True,
                              check=True)
        
        # Print output
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:", result.stderr)
            
        return True
    
    except subprocess.CalledProcessError as e:
        print(f"Error executing {script_path}:")
        print(e.stdout)
        print("STDERR:", e.stderr)
        return False
    
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """
    Main function to run both the preprocessing and showcase update scripts.
    """
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct paths to the other scripts
    preprocess_script = os.path.join(script_dir, "preprocess_reports.py")
    update_showcase_script = os.path.join(script_dir, "update_showcase.py")
    
    # Check if the scripts exist
    for script_path in [preprocess_script, update_showcase_script]:
        if not os.path.exists(script_path):
            print(f"Script {script_path} not found.")
            return False
    
    # First run the preprocessing script
    if not run_script(preprocess_script):
        print("Preprocessing failed. Stopping.")
        return False
    
    # Then run the showcase update script
    if not run_script(update_showcase_script):
        print("Showcase update failed.")
        return False
    
    print("\n=== All done! ===")
    print("1. The Sway headers and social share banners have been removed from all instructor report HTML files.")
    print("2. The showcase has been updated with all the preprocessed reports.")
    print("\nBackups of the original files have been created in:")
    print("- instructor_reports_backup (for the individual report files)")
    print("- instructor_reports_showcase_backup.html (for the showcase file)")
    
    return True

if __name__ == "__main__":
    main() 