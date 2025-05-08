#!/bin/bash

# Sway Reports Update Script
# This script makes it easy to update the instructor reports showcase

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to display the menu
show_menu() {
    clear
    echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║       ${GREEN}Sway Reports Showcase Updater${BLUE}        ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
    echo
    echo -e "${YELLOW}1.${NC} Update showcase (preserve all manual work)"
    echo -e "${YELLOW}2.${NC} Update showcase AND refresh existing reports"
    echo -e "${YELLOW}3.${NC} Recover from backup"
    echo -e "${YELLOW}4.${NC} Exit"
    echo
    echo -e "${BLUE}By default, all your manual categorization and ordering work is preserved.${NC}"
    echo
}

# Function to run the update with preservation
run_update_preserve() {
    echo -e "${GREEN}Running update while preserving all manual work...${NC}"
    python3 update_showcase.py
    echo
    echo -e "${GREEN}Update complete! All your manual work has been preserved.${NC}"
    echo -e "${BLUE}New reports have been added with auto-extracted titles, descriptions, and categories.${NC}"
    echo
    read -p "Press Enter to continue..."
}

# Function to run the update with refresh
run_update_refresh() {
    echo -e "${YELLOW}WARNING: This will refresh ALL report titles, descriptions, and categories from HTML files.${NC}"
    echo -e "${BLUE}Your report ordering and enabled/disabled settings will still be preserved.${NC}"
    echo
    read -p "Are you sure you want to continue? (y/n) " choice
    
    if [[ $choice == "y" || $choice == "Y" ]]; then
        echo -e "${GREEN}Running update with refresh...${NC}"
        python3 update_showcase.py --refresh-existing
        echo
        echo -e "${GREEN}Update complete! Report data has been refreshed from HTML files.${NC}"
    else
        echo -e "${BLUE}Refresh canceled.${NC}"
    fi
    
    echo
    read -p "Press Enter to continue..."
}

# Function to run the recovery script
run_recovery() {
    echo -e "${YELLOW}Running recovery script...${NC}"
    echo -e "${BLUE}This will show all available backups and let you choose which one to recover from.${NC}"
    echo
    python3 recover_showcase_data.py
    echo
    read -p "Press Enter to continue..."
}

# Main loop
while true; do
    show_menu
    read -p "Enter your choice (1-4): " choice
    
    case $choice in
        1)
            run_update_preserve
            ;;
        2)
            run_update_refresh
            ;;
        3)
            run_recovery
            ;;
        4)
            echo -e "${GREEN}Goodbye!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice. Please try again.${NC}"
            sleep 1
            ;;
    esac
done 