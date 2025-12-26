import duckdb
from datetime import datetime
from database import db, create_tables

from user_menu import register_user, login_user, setup_wardrobe, main_menu
from item_management import view_all_items, add_clothing_item, remove_clothing_item, search_filter_items
from wear_entry_management import (
    view_wear_history, 
    add_wear_entry, 
    remove_wear_entry,
    search_filter_wear_entry
)
from analytics_management import wear_count_analytics, wardrobe_composition_analytics, investment_analytics


# Initialize database connection and create tables
create_tables()

def main():
    print("Welcome to Smart Wardrobe Tracker!")
    
    while True:
        print("\n1. Register")
        print("2. Login")
        print("3. Exit")
        
        choice = input("Enter your choice: ")
        
        if choice == '1':
            user_id = register_user()
            if user_id:
                setup_wardrobe(user_id)
                main_menu(user_id)
        elif choice == '2':
            user_id = login_user()
            if user_id:
                main_menu(user_id)
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
