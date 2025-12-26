from database import db
import re
from datetime import datetime

from item_management import view_all_items, add_clothing_item, remove_clothing_item, search_filter_items
from wear_entry_management import (
    view_wear_history, 
    add_wear_entry, 
    remove_wear_entry,
    search_filter_wear_entry
)
from analytics_management import wear_count_analytics, wardrobe_composition_analytics, investment_analytics

def register_user():
    print("\n=== Register New Account ===")
    
    while True:
        name = input("Enter your name: ").strip()
        if name:
            break
        print("Name cannot be empty.")
    
    while True:
        email = input("Enter your email: ").strip()
        if not email:
            print("Email cannot be empty.")
            continue
        
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            print("Invalid email format. Please try again.")
            continue
            
        if db.execute("SELECT user_id FROM Users WHERE email = ?", [email]).fetchone():
            print("Email already registered. Please use a different email.")
            continue
        break
    
    while True:
        print("Password must be at least 8 characters long")
        password = input("Enter your password: ")
        if len(password) >= 8:
            break
        print("Password too short. Please try again.")
    
    try:
        last_user = db.execute("SELECT MAX(user_id) FROM Users").fetchone()[0]
        new_user_id = 1 if last_user is None else last_user + 1
        
        db.execute("""
            INSERT INTO Users (user_id, name, email, password)
            VALUES (?, ?, ?, ?)
        """, (new_user_id, name, email, password))
        
        print("\nRegistration successful! Please log in to continue.")
        return new_user_id
        
    except Exception as e:
        print(f"Error during registration: {str(e)}")
        return None

def login_user():
    print("\n=== Login ===")
    while True:
        email = input("Enter your email: ")
        password = input("Enter your password: ")
        
        user = db.execute("""
            SELECT user_id, name 
            FROM Users 
            WHERE email = ? AND password = ?
        """, (email, password)).fetchone()
        
        if user:
            print(f"\nWelcome back!")
            return user[0]
        else:
            print("Invalid email or password.")
            retry = input("Would you like to try again? (y/n): ")
            if retry.lower() != 'y':
                return None

def setup_wardrobe(user_id):
    print("\nLet's set up your wardrobe categories!")
    print("What are the categories that you'd like to add in your wardrobe?")
    print("(Please add at least 3 categories)")
    
    categories = []
    while len(categories) < 3:
        category = input(f"Enter category {len(categories) + 1}: ").strip()
        if category and category not in categories:
            categories.append(category)
    
    for category in categories:
        last_id = db.execute("SELECT MAX(category_id) FROM Categories").fetchone()[0]
        new_id = 1 if last_id is None else last_id + 1
        db.execute("INSERT INTO Categories (category_id, user_id, name) VALUES (?, ?, ?)", 
                  (new_id, user_id, category))
    
    print("\nWhat are the colors that you usually wear?")
    print("(Please add at least 3 colors)")
    
    colors = []
    while len(colors) < 3:
        color = input(f"Enter color {len(colors) + 1}: ").strip()
        if color and color not in colors:
            colors.append(color)
    
    for color in colors:
        last_id = db.execute("SELECT MAX(color_id) FROM Colors").fetchone()[0]
        new_id = 1 if last_id is None else last_id + 1
        db.execute("INSERT INTO Colors (color_id, user_id, name) VALUES (?, ?, ?)", 
                  (new_id, user_id, color))
    
    print("\nWhat sizes do you usually wear?")
    print("(Please add at least 2 sizes)")
    
    sizes = []
    while len(sizes) < 2:
        size = input(f"Enter size {len(sizes) + 1}: ").strip()
        if size and size not in sizes:
            sizes.append(size)
    
    for size in sizes:
        last_id = db.execute("SELECT MAX(size_id) FROM Sizes").fetchone()[0]
        new_id = 1 if last_id is None else last_id + 1
        db.execute("INSERT INTO Sizes (size_id, user_id, name) VALUES (?, ?, ?)", 
                  (new_id, user_id, size))
    
    print("\nWhat brands do you usually buy?")
    print("(Please add at least 3 brands)")
    
    brands = []
    while len(brands) < 3:
        brand = input(f"Enter brand {len(brands) + 1}: ").strip()
        if brand and brand not in brands:
            brands.append(brand)
    
    for brand in brands:
        last_id = db.execute("SELECT MAX(brand_id) FROM Brands").fetchone()[0]
        new_id = 1 if last_id is None else last_id + 1
        db.execute("INSERT INTO Brands (brand_id, user_id, name) VALUES (?, ?, ?)", 
                  (new_id, user_id, brand))
    
    print("\nWardrobe setup completed successfully!")

def main_menu(user_id):
    while True:
        print("\n=== Main Menu ===")
        
        print("\nClothing Menu:")
        print("1. View All Clothing Items")
        print("2. Add a Clothing Item")
        print("3. Remove a Clothing Item")
        print("4. Search/Filter Items")
        
        print("\nWear Log Menu:")
        print("5. View Wear History")
        print("6. Add Wear Entry")
        print("7. Remove Wear Entry")
        print("8. Search/Filter Wear Logs")
        
        print("\nAnalytics Menu:")
        print("9. Wear Count Analytics")
        print("10. Wardrobe Composition Analytics")
        print("11. Investment Analytics")
        print("12. Back to Main Menu")
        
        choice = input("\nEnter your choice: ")
        
        try:
            if choice == '1':
                view_all_items(user_id)
            elif choice == '2':
                add_clothing_item(user_id)
            elif choice == '3':
                remove_clothing_item(user_id)
            elif choice == '4':
                search_filter_items(user_id)
            elif choice == '5':
                view_wear_history(user_id)
            elif choice == '6':
                add_wear_entry(user_id)
            elif choice == '7':
                remove_wear_entry(user_id)
            elif choice == '8':
                search_filter_wear_entry(user_id)
            elif choice == '9':
                wear_count_analytics(db, user_id)
            elif choice == '10':
                wardrobe_composition_analytics(db, user_id)
            elif choice == '11':
                investment_analytics(db, user_id)
            elif choice == '12':
                break
            else:
                print("Invalid choice. Please try again.")
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            print("Returning to Main Menu...")
