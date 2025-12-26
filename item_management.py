from database import db
from datetime import datetime

def view_all_items(user_id):
    print("\n=== All Clothing Items ===")
    
    items = db.execute("""
        SELECT i.item_id, i.name, c.name as category, co.name as color, 
               s.name as size, b.name as brand, 
               i.purchase_date, CASE 
                   WHEN i.price IS NULL OR i.price = 0 THEN NULL 
                   ELSE i.price 
               END as price
        FROM Clothing_Items i
        JOIN Categories c ON i.category_id = c.category_id
        JOIN Colors co ON i.color_id = co.color_id
        JOIN Sizes s ON i.size_id = s.size_id
        JOIN Brands b ON i.brand_id = b.brand_id
        WHERE i.user_id = ?
        ORDER BY c.category_id ASC, i.name
    """, [user_id]).fetchall()
    
    if not items:
        print("No items found in your wardrobe.")
        return
    
    print(f"\n{'#':<3} | {'Category':<9} | {'Name':<12} | {'Color':<7} | {'Size':<4} | {'Brand':<9} | {'Price':<9} | {'Purchased':<10}")
    print("-" * 82)
    
    for i, item in enumerate(items, 1):
        category = item[2][:9]
        name = (item[1][:10] + '..') if len(item[1]) > 12 else item[1]
        color = item[3][:7]
        size = item[4][:4]
        brand = item[5][:9]
        price_display = f"${item[7]:.2f}" if item[7] is not None else "N/A"
        date = str(item[6]) if item[6] else "N/A"
        
        print("{:<3} | {:<9} | {:<12} | {:<7} | {:<4} | {:<9} | {:<9} | {:<10}".format(
            i, category, name, color, size, brand, price_display, date))


def add_clothing_item(user_id):
    print("\n=== Add New Clothing Item ===")
    name = input("Enter item name: ")
    
    # Get category
    print("\nSelect category:")
    print("0. Add new category")
    categories = db.execute("SELECT category_id, name FROM Categories WHERE user_id = ?", 
                          [user_id]).fetchall()
    for i, category in enumerate(categories, 1):
        print(f"{i}. {category[1]}")
    
    category_choice = input("Enter category number: ")
    if category_choice == '0':
        category_name = input("Enter new category name: ")
        last_id = db.execute("SELECT MAX(category_id) FROM Categories").fetchone()[0]
        category_id = 1 if last_id is None else last_id + 1
        db.execute("INSERT INTO Categories (category_id, user_id, name) VALUES (?, ?, ?)", 
                  (category_id, user_id, category_name))
    else:
        category_id = categories[int(category_choice)-1][0]
    
    # Get or add color
    colors = db.execute("SELECT * FROM Colors WHERE user_id = ?", [user_id]).fetchall()
    print("\nSelect color:")
    print("0. Add new color")
    for i, color in enumerate(colors, 1):
        print(f"{i}. {color[2]}")
    
    while True:
        try:
            choice = int(input("Enter color number: "))
            if choice == 0:
                new_color = input("Enter new color name: ").strip()
                if new_color:
                    last_id = db.execute("SELECT MAX(color_id) FROM Colors").fetchone()[0]
                    new_color_id = 1 if last_id is None else last_id + 1
                    db.execute("INSERT INTO Colors (color_id, user_id, name) VALUES (?, ?, ?)",
                             (new_color_id, user_id, new_color))
                    color_id = new_color_id
                    break
            elif 1 <= choice <= len(colors):
                color_id = colors[choice-1][0]
                break
        except ValueError:
            pass
        print("Invalid choice. Please try again.")
    
    # Get or add size
    sizes = db.execute("SELECT * FROM Sizes WHERE user_id = ?", [user_id]).fetchall()
    print("\nSelect size:")
    print("0. Add new size")
    for i, size in enumerate(sizes, 1):
        print(f"{i}. {size[2]}")
    
    while True:
        try:
            choice = int(input("Enter size number: "))
            if choice == 0:
                new_size = input("Enter new size name: ").strip()
                if new_size:
                    last_id = db.execute("SELECT MAX(size_id) FROM Sizes").fetchone()[0]
                    new_size_id = 1 if last_id is None else last_id + 1
                    db.execute("INSERT INTO Sizes (size_id, user_id, name) VALUES (?, ?, ?)",
                             (new_size_id, user_id, new_size))
                    size_id = new_size_id
                    break
            elif 1 <= choice <= len(sizes):
                size_id = sizes[choice-1][0]
                break
        except ValueError:
            pass
        print("Invalid choice. Please try again.")
    
    # Get or add brand
    brands = db.execute("SELECT * FROM Brands WHERE user_id = ?", [user_id]).fetchall()
    print("\nSelect brand:")
    print("0. Add new brand")
    for i, brand in enumerate(brands, 1):
        print(f"{i}. {brand[2]}")
    
    while True:
        try:
            choice = int(input("Enter brand number: "))
            if choice == 0:
                new_brand = input("Enter new brand name: ").strip()
                if new_brand:
                    last_id = db.execute("SELECT MAX(brand_id) FROM Brands").fetchone()[0]
                    new_brand_id = 1 if last_id is None else last_id + 1
                    db.execute("INSERT INTO Brands (brand_id, user_id, name) VALUES (?, ?, ?)",
                             (new_brand_id, user_id, new_brand))
                    brand_id = new_brand_id
                    break
            elif 1 <= choice <= len(brands):
                brand_id = brands[choice-1][0]
                break
        except ValueError:
            pass
        print("Invalid choice. Please try again.")
    
    
    # Add price input
    while True:
        try:
            price_input = input("\nEnter price (press Enter if unknown): ").strip()
            if price_input == "":
                price = None
                break
            price = float(price_input)
            if price >= 0:
                break
            print("Price must be non-negative.")
        except ValueError:
            print("Invalid price. Please enter a number or press Enter if unknown.")

    # Get purchase date
    while True:
        date_str = input("\nEnter purchase date (dd/mm/yyyy) or press Enter for today: ")
        if not date_str:
            purchase_date = datetime.now().strftime('%Y-%m-%d')
            break
        try:
            date_obj = datetime.strptime(date_str, '%d/%m/%Y')
            purchase_date = date_obj.strftime('%Y-%m-%d')
            break
        except ValueError:
            print("Invalid date format. Please use dd/mm/yyyy")

    try:
        # Insert new item without wear_count
        last_id = db.execute("SELECT MAX(item_id) FROM Clothing_Items").fetchone()[0]
        item_id = 1 if last_id is None else last_id + 1
        
        db.execute("""
            INSERT INTO Clothing_Items (
                item_id, user_id, name, category_id, color_id, 
                size_id, brand_id, purchase_date, price
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (item_id, user_id, name, category_id, color_id, 
              size_id, brand_id, purchase_date, price))
        
        print("\nItem added successfully!")
        
    except Exception as e:
        print(f"Error adding clothing item: {e}")


def remove_clothing_item(user_id):
    print("\n=== Remove Clothing Item ===")
    
    items = db.execute("""
        SELECT i.item_id, i.name, c.name as category, co.name as color, 
               s.name as size, b.name as brand, 
               i.purchase_date, i.price
        FROM Clothing_Items i
        JOIN Categories c ON i.category_id = c.category_id
        JOIN Colors co ON i.color_id = co.color_id
        JOIN Sizes s ON i.size_id = s.size_id
        JOIN Brands b ON i.brand_id = b.brand_id
        WHERE i.user_id = ?
        ORDER BY c.name, i.name
    """, [user_id]).fetchall()
    
    if not items:
        print("No items found in your wardrobe.")
        return
    
    print("\nSelect item to remove:")
    print("0. Back to Main Menu")
    
    print(f"\n{'#':<3} | {'Category':<9} | {'Name':<12} | {'Color':<7} | {'Size':<4} | {'Brand':<9} | {'Price':<9} | {'Purchased':<10}")
    print("-" * 82)
    
    for i, item in enumerate(items, 1):
        category = item[2][:9]
        name = (item[1][:10] + '..') if len(item[1]) > 12 else item[1]
        color = item[3][:7]
        size = item[4][:4]
        brand = item[5][:9]
        price_display = f"${item[7]:.2f}" if item[7] is not None else "N/A"
        date = str(item[6]) if item[6] else "N/A"
        
        print("{:<3} | {:<9} | {:<12} | {:<7} | {:<4} | {:<9} | {:<9} | {:<10}".format(
            i, category, name, color, size, brand, price_display, date))
    
    while True:
        try:
            choice = int(input("\nEnter item number: "))
            if choice == 0:
                return
            if 1 <= choice <= len(items):
                item_id = items[choice-1][0]
                break
        except ValueError:
            pass
        print("Invalid choice. Please try again.")
    
    confirm = input(f"\nAre you sure you want to remove {items[choice-1][1]}? (y/n): ")
    if confirm.lower() == 'y':
        # Delete associated wear logs first
        db.execute("DELETE FROM Wear_Logs WHERE item_id = ?", [item_id])
        # Then delete the item
        db.execute("DELETE FROM Clothing_Items WHERE item_id = ?", [item_id])
        print("\nItem removed successfully!")
    else:
        print("\nOperation cancelled.")


def search_filter_items(user_id):
    print("\n=== Search/Filter Items ===")
    print("Filter by:")
    print("0. Back to Main Menu")
    print("1. Category")
    print("2. Color")
    print("3. Size")
    print("4. Brand")
    print("5. Purchase Date")
    
    choice = input("Enter choice: ")
    
    if choice == '0':
        return

    if choice in ["1", "2", "3", "4"]:
        tables = {
            "1": ("Categories", "category"),
            "2": ("Colors", "color"),
            "3": ("Sizes", "size"),
            "4": ("Brands", "brand")
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
        
        items = db.execute(f"""
            SELECT i.name, c.name as category, co.name as color, 
                   s.name as size, b.name as brand, i.purchase_date, i.price
            FROM Clothing_Items i
            JOIN Categories c ON i.category_id = c.category_id
            JOIN Colors co ON i.color_id = co.color_id
            JOIN Sizes s ON i.size_id = s.size_id
            JOIN Brands b ON i.brand_id = b.brand_id
            WHERE i.user_id = ? AND i.{id_field} = ?
            ORDER BY i.name
        """, (user_id, filter_id)).fetchall()
        
    elif choice == "5":
        print("\nFilter by:")
        print("1. Specific date")
        print("2. Date range")
        date_choice = input("Enter choice: ")
        
        if date_choice == "1":
            while True:
                date_str = input("Enter date (dd/mm/yyyy): ")
                try:
                    date_obj = datetime.strptime(date_str, '%d/%m/%Y')
                    filter_date = date_obj.strftime('%Y-%m-%d')
                    break
                except ValueError:
                    print("Invalid date format. Please use dd/mm/yyyy")
            
            items = db.execute("""
                SELECT i.name, c.name as category, co.name as color, 
                       s.name as size, b.name as brand, i.purchase_date, i.price
                FROM Clothing_Items i
                JOIN Categories c ON i.category_id = c.category_id
                JOIN Colors co ON i.color_id = co.color_id
                JOIN Sizes s ON i.size_id = s.size_id
                JOIN Brands b ON i.brand_id = b.brand_id
                WHERE i.user_id = ? AND i.purchase_date = ?
                ORDER BY i.name
            """, (user_id, filter_date)).fetchall()
            
        elif date_choice == "2":
            while True:
                start_date_str = input("Enter start date (dd/mm/yyyy): ")
                try:
                    start_date_obj = datetime.strptime(start_date_str, '%d/%m/%Y')
                    start_date = start_date_obj.strftime('%Y-%m-%d')
                    break
                except ValueError:
                    print("Invalid date format. Please use dd/mm/yyyy")
            
            while True:
                end_date_str = input("Enter end date (dd/mm/yyyy): ")
                try:
                    end_date_obj = datetime.strptime(end_date_str, '%d/%m/%Y')
                    end_date = end_date_obj.strftime('%Y-%m-%d')
                    break
                except ValueError:
                    print("Invalid date format. Please use dd/mm/yyyy")
            
            items = db.execute("""
                SELECT i.name, c.name as category, co.name as color, 
                       s.name as size, b.name as brand, i.purchase_date, i.price
                FROM Clothing_Items i
                JOIN Categories c ON i.category_id = c.category_id
                JOIN Colors co ON i.color_id = co.color_id
                JOIN Sizes s ON i.size_id = s.size_id
                JOIN Brands b ON i.brand_id = b.brand_id
                WHERE i.user_id = ? AND i.purchase_date BETWEEN CAST(? AS DATE) AND CAST(? AS DATE)
                ORDER BY i.name
            """, (user_id, start_date, end_date)).fetchall()
    
    if not items:
        print("\nNo items found matching the filter criteria.")
        return
    
    # Define columns
    all_cols = {
        'category': ('Category', 9),
        'name':     ('Name', 12),
        'color':    ('Color', 7),
        'size':     ('Size', 4),
        'brand':    ('Brand', 9),
        'price':    ('Price', 9),
        'date':     ('Purchased', 10)
    }

    # Determine columns to display
    standard_order = ['name', 'category', 'color', 'size', 'brand', 'price', 'date']

    if choice in ['1', '2', '3', '4']:
        # For Category, Color, Size, Brand filters, exclude the filtered column
        exclude_map = {'1': 'category', '2': 'color', '3': 'size', '4': 'brand'}
        excluded_key = exclude_map.get(choice)
        col_order = [k for k in standard_order if k != excluded_key]
    else:
        # For Purchase Date (5), show all columns
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
    for i, item in enumerate(items, 1):
        # Map item data
        row_data = {
            'name': (item[0][:10] + '..') if len(item[0]) > 12 else item[0],
            'category': item[1][:9],
            'color': item[2][:7],
            'size': item[3][:4],
            'brand': item[4][:9],
            'date': str(item[5]) if item[5] else "N/A",
            'price': f"${item[6]:.2f}" if item[6] is not None else "N/A"
        }
        
        row_parts = [f"{i:<3}"]
        for key in col_order:
            val = row_data[key]
            width = all_cols[key][1]
            row_parts.append(f"{val:<{width}}")
            
        print(" | ".join(row_parts))