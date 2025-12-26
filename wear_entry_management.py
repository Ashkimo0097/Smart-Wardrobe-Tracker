from database import db
from datetime import datetime

def view_wear_history(user_id):
    print("\n=== Wear History ===")
    
    logs = db.execute("""
        SELECT w.wear_date, i.name as item_name, c.name as category, 
               co.name as color, s.name as size, b.name as brand
        FROM Wear_Logs w
        JOIN Clothing_Items i ON w.item_id = i.item_id
        JOIN Categories c ON i.category_id = c.category_id
        JOIN Colors co ON i.color_id = co.color_id
        JOIN Sizes s ON i.size_id = s.size_id
        JOIN Brands b ON i.brand_id = b.brand_id
        WHERE w.user_id = ?
        ORDER BY w.wear_date DESC
    """, [user_id]).fetchall()
    
    if not logs:
        print("No wear history found.")
        return
    
    print(f"\n{'#':<3} | {'Date':<10} | {'Name':<12} | {'Category':<9} | {'Color':<7} | {'Size':<4} | {'Brand':<9}")
    print("-" * 75)
    
    for i, log in enumerate(logs, 1):
        date = str(log[0])
        name = (log[1][:10] + '..') if len(log[1]) > 12 else log[1]
        category = log[2][:9]
        color = log[3][:7]
        size = log[4][:4]
        brand = log[5][:9]
        
        print("{:<3} | {:<10} | {:<12} | {:<9} | {:<7} | {:<4} | {:<9}".format(
            i, date, name, category, color, size, brand))

def add_wear_entry(user_id):
    print("\n=== Log Item Wear ===")
    
    # Get all items for the user
    items = db.execute("""
        SELECT i.item_id, i.name, c.name as category
        FROM Clothing_Items i
        JOIN Categories c ON i.category_id = c.category_id
        WHERE i.user_id = ?
        ORDER BY c.name, i.name
    """, [user_id]).fetchall()
    
    if not items:
        print("No items found in your wardrobe.")
        return
    
    # Display items
    print("\nSelect item:")
    print("0. Back to Main Menu")
    for i, item in enumerate(items, 1):
        print(f"{i}. {item[1]} ({item[2]})")
    
    # Get item selection
    while True:
        try:
            choice = int(input("\nEnter item number: "))
            if choice == 0:
                return
            if 1 <= choice <= len(items):
                item_id = items[choice-1][0]
                break
            print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a number.")
    
    # Get wear date
    while True:
        date_str = input("\nEnter wear date (dd/mm/yyyy) or press Enter for today: ")
        if not date_str:
            wear_date = datetime.now().strftime('%Y-%m-%d')
            break
        try:
            date_obj = datetime.strptime(date_str, '%d/%m/%Y')
            wear_date = date_obj.strftime('%Y-%m-%d')
            break
        except ValueError:
            print("Invalid date format. Please use dd/mm/yyyy")
    
    try:
        last_id = db.execute("SELECT MAX(wear_id) FROM Wear_Logs").fetchone()[0]
        wear_id = 1 if last_id is None else last_id + 1
        
        db.execute("""
            INSERT INTO Wear_Logs (wear_id, user_id, item_id, wear_date)
            VALUES (?, ?, ?, ?)
        """, (wear_id, user_id, item_id, wear_date))
        
        print(f"\nWear logged successfully for {items[choice-1][1]} on {wear_date}!")
        
    except Exception as e:
        print(f"Error logging wear: {e}")

def remove_wear_entry(user_id):
    print("\n=== Remove Wear Log Entry ===")
    
    logs = db.execute("""
        SELECT l.wear_id, l.wear_date, i.name as item_name, c.name as category, 
               co.name as color, s.name as size, b.name as brand
        FROM Wear_Logs l
        JOIN Clothing_Items i ON l.item_id = i.item_id
        JOIN Categories c ON i.category_id = c.category_id
        JOIN Colors co ON i.color_id = co.color_id
        JOIN Sizes s ON i.size_id = s.size_id
        JOIN Brands b ON i.brand_id = b.brand_id
        WHERE l.user_id = ?
        ORDER BY l.wear_date DESC
    """, [user_id]).fetchall()
    
    if not logs:
        print("No wear logs found.")
        return
    
    print("\nSelect log to remove:")
    print("0. Back to Main Menu")
    
    print(f"\n{'#':<3} | {'Date':<10} | {'Name':<12} | {'Category':<9} | {'Color':<7} | {'Size':<4} | {'Brand':<9}")
    print("-" * 75)
    
    for i, log in enumerate(logs, 1):
        date = str(log[1])
        name = (log[2][:10] + '..') if len(log[2]) > 12 else log[2]
        category = log[3][:9]
        color = log[4][:7]
        size = log[5][:4]
        brand = log[6][:9]
        
        print("{:<3} | {:<10} | {:<12} | {:<9} | {:<7} | {:<4} | {:<9}".format(
            i, date, name, category, color, size, brand))
    
    while True:
        try:
            choice = int(input("\nEnter log number: "))
            if choice == 0:
                return
            if 1 <= choice <= len(logs):
                selected_log = logs[choice-1]
                break
        except ValueError:
            pass
        print("Invalid choice. Please try again.")
    
    confirm = input(f"\nAre you sure you want to remove this wear log? (y/n): ")
    if confirm.lower() == 'y':
        db.execute("DELETE FROM Wear_Logs WHERE wear_id = ?", [selected_log[0]])
        print("\nWear log removed successfully!")
    else:
        print("\nOperation cancelled.")

def search_filter_wear_entry(user_id):
    print("\n=== Search/Filter Wear Logs ===")
    print("Filter by:")
    print("0. Back to Main Menu")
    print("1. Item Name")
    print("2. Category")
    print("3. Color")
    print("4. Size")
    print("5. Brand")
    print("6. Wear Date Range")
    
    choice = input("Enter choice: ")
    
    if choice == '0':
        return

    if choice == '1':
        # Fetch items with full details for the selection table
        items = db.execute("""
            SELECT DISTINCT i.item_id, i.name, c.name as category, 
                   co.name as color, s.name as size, b.name as brand
            FROM Clothing_Items i
            JOIN Wear_Logs l ON i.item_id = l.item_id
            JOIN Categories c ON i.category_id = c.category_id
            JOIN Colors co ON i.color_id = co.color_id
            JOIN Sizes s ON i.size_id = s.size_id
            JOIN Brands b ON i.brand_id = b.brand_id
            WHERE i.user_id = ?
            ORDER BY i.name
        """, [user_id]).fetchall()
        
        print("\nSelect item:")
        print("0. Back to Main Menu")
        
        # Display Item Selection Table
        print(f"\n{'#':<3} | {'Name':<12} | {'Category':<9} | {'Color':<7} | {'Size':<4} | {'Brand':<9}")
        print("-" * 60)
        
        for i, item in enumerate(items, 1):
            name = (item[1][:10] + '..') if len(item[1]) > 12 else item[1]
            category = item[2][:9]
            color = item[3][:7]
            size = item[4][:4]
            brand = item[5][:9]
            print(f"{i:<3} | {name:<12} | {category:<9} | {color:<7} | {size:<4} | {brand:<9}")
        
        while True:
            try:
                item_choice = int(input("\nEnter item number: "))
                if item_choice == 0:
                    return
                if 1 <= item_choice <= len(items):
                    item_id = items[item_choice-1][0]
                    selected_item_name = items[item_choice-1][1]
                    break
            except ValueError:
                pass
            print("Invalid choice. Please try again.")
        
        # Fetch only dates for the selected item
        dates = db.execute("""
            SELECT wear_date
            FROM Wear_Logs
            WHERE item_id = ? AND user_id = ?
            ORDER BY wear_date DESC
        """, (item_id, user_id)).fetchall()
        
        if not dates:
            print("\nNo wear logs found for this item.")
        else:
            print(f"\nWear Dates for {selected_item_name}:")
            for date in dates:
                print(f"- {date[0]}")
        return

    # Logic for other filters (Date Range, Category, Color, etc.)
    logs = []
    
    if choice == '6':
        while True:
            try:
                start_date = input("Enter start date (dd/mm/yyyy): ")
                end_date = input("Enter end date (dd/mm/yyyy): ")
                start_obj = datetime.strptime(start_date, '%d/%m/%Y')
                end_obj = datetime.strptime(end_date, '%d/%m/%Y')
                start = start_obj.strftime('%Y-%m-%d')
                end = end_obj.strftime('%Y-%m-%d')
                break
            except ValueError:
                print("Invalid date format. Please use dd/mm/yyyy")
        
        logs = db.execute("""
            SELECT w.wear_date, i.name, c.name as category, 
                   co.name as color, s.name as size, b.name as brand
            FROM Wear_Logs w
            JOIN Clothing_Items i ON w.item_id = i.item_id
            JOIN Categories c ON i.category_id = c.category_id
            JOIN Colors co ON i.color_id = co.color_id
            JOIN Sizes s ON i.size_id = s.size_id
            JOIN Brands b ON i.brand_id = b.brand_id
            WHERE w.user_id = ? AND w.wear_date BETWEEN CAST(? AS DATE) AND CAST(? AS DATE)
            ORDER BY w.wear_date DESC
        """, (user_id, start, end)).fetchall()

    elif choice in ["2", "3", "4", "5"]:
        tables = {
            "2": ("Categories", "category"),
            "3": ("Colors", "color"),
            "4": ("Sizes", "size"),
            "5": ("Brands", "brand")
        }
        
        table_name, field_name = tables[choice]
        options = db.execute(f"SELECT * FROM {table_name} WHERE user_id = ?", 
                           [user_id]).fetchall()
        
        print(f"\nSelect {field_name}:")
        for i, option in enumerate(options, 1):
            print(f"{i}. {option[2]}")
        
        while True:
            try:
                filter_choice = int(input("Enter number: "))
                if 1 <= filter_choice <= len(options):
                    filter_id = options[filter_choice-1][0]
                    id_field = f"{field_name}_id"
                    break
            except ValueError:
                pass
            print("Invalid choice. Please try again.")
            
        logs = db.execute(f"""
            SELECT w.wear_date, i.name, c.name as category, 
                   co.name as color, s.name as size, b.name as brand
            FROM Wear_Logs w
            JOIN Clothing_Items i ON w.item_id = i.item_id
            JOIN Categories c ON i.category_id = c.category_id
            JOIN Colors co ON i.color_id = co.color_id
            JOIN Sizes s ON i.size_id = s.size_id
            JOIN Brands b ON i.brand_id = b.brand_id
            WHERE w.user_id = ? AND i.{id_field} = ?
            ORDER BY w.wear_date DESC
        """, (user_id, filter_id)).fetchall()
    
    if not logs:
        print("\nNo matching wear logs found.")
        return
    
    # Define columns
    all_cols = {
        'date':     ('Date', 10),
        'name':     ('Name', 12),
        'category': ('Category', 9),
        'color':    ('Color', 7),
        'size':     ('Size', 4),
        'brand':    ('Brand', 9)
    }

    # Determine columns to display
    standard_order = ['date', 'name', 'category', 'color', 'size', 'brand']
    
    if choice in ['2', '3', '4', '5']:
        # For Category, Color, Size, Brand filters, exclude the filtered column
        exclude_map = {'2': 'category', '3': 'color', '4': 'size', '5': 'brand'}
        excluded_key = exclude_map.get(choice)
        col_order = [k for k in standard_order if k != excluded_key]
    else:
        # For Date Range (6), show all columns
        col_order = standard_order
    
    # Print Header
    header_parts = [f"{'#':<3}"]
    for key in col_order:
        header, width = all_cols[key]
        header_parts.append(f"{header:<{width}}")
    header_str = " | ".join(header_parts)
    print("\n" + header_str)
    print("-" * len(header_str))
    
    # Print Rows
    for i, log in enumerate(logs, 1):
        # Map log data
        row_data = {
            'date': str(log[0]),
            'name': (log[1][:10] + '..') if len(log[1]) > 12 else log[1],
            'category': log[2][:9],
            'color': log[3][:7],
            'size': log[4][:4],
            'brand': log[5][:9]
        }
        
        row_parts = [f"{i:<3}"]
        for key in col_order:
            val = row_data[key]
            width = all_cols[key][1]
            row_parts.append(f"{val:<{width}}")
            
        print(" | ".join(row_parts))
