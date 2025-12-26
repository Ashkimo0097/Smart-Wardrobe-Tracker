from database import db
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import calendar

def wear_count_analytics(db, user_id):
    print("\nAnalyze by:")
    print("0. Back to Main Menu")
    print("1. Category")
    print("2. Color")
    print("3. Size")
    print("4. Brand")
    print("5. All Items")
    
    analysis_type = input("\nEnter your choice: ")
    
    try:
        if analysis_type == '0':
            return
        elif analysis_type == '5':  # All items
            results = db.execute("""
                SELECT 
                    i.name as item_name,
                    c.name as color_name,
                    b.name as brand_name,
                    i.price,
                    COUNT(w.wear_id) as wear_count
                FROM Clothing_Items i
                LEFT JOIN Wear_Logs w ON i.item_id = w.item_id
                LEFT JOIN Colors c ON i.color_id = c.color_id
                LEFT JOIN Brands b ON i.brand_id = b.brand_id
                WHERE i.user_id = ?
                GROUP BY i.item_id, i.name, c.name, b.name, i.price
                ORDER BY wear_count DESC
            """, [user_id]).fetchall()
            
            if not results:
                print("\nNo items found.")
                return
            
            print("\nWear counts for all items:")
            # Header
            header = f"{'#':<3} | {'Item Name':<20} | {'Color':<10} | {'Brand':<10} | {'Price':<10} | {'Wear Count':<10}"
            print("\n" + header)
            print("-" * len(header))
            
            plot_data = []
            for i, row in enumerate(results, 1):
                item_name = (row[0][:17] + '..') if len(row[0]) > 17 else row[0]
                color = row[1] if row[1] else "N/A"
                brand = row[2] if row[2] else "N/A"
                price = f"${row[3]:.2f}" if row[3] is not None else "N/A"
                count = row[4]
                
                print(f"{i:<3} | {item_name:<20} | {color:<10} | {brand:<10} | {price:<10} | {count:<10}")
                plot_data.append((row[0], count))
            
            if plot_data:
                names = [x[0] for x in plot_data]
                counts = [x[1] for x in plot_data]
                
                plt.figure(figsize=(12, 6))
                plt.bar(names, counts, color='skyblue')
                plt.title('Wear Counts - All Items')
                plt.xlabel('Item')
                plt.ylabel('Wear Count')
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                plt.show()
                
        elif analysis_type in ['1', '2', '3', '4']:
            # Configuration
            config = {
                '1': {'table': 'Categories', 'id': 'category_id', 'label': 'Category', 
                      'cols': ['Item Name', 'Color', 'Brand', 'Wear Count']},
                '2': {'table': 'Colors', 'id': 'color_id', 'label': 'Color',
                      'cols': ['Item Name', 'Category', 'Brand', 'Wear Count']},
                '3': {'table': 'Sizes', 'id': 'size_id', 'label': 'Size',
                      'cols': ['Item Name', 'Category', 'Color', 'Brand', 'Wear Count']},
                '4': {'table': 'Brands', 'id': 'brand_id', 'label': 'Brand',
                      'cols': ['Item Name', 'Category', 'Color', 'Wear Count']}
            }
            
            conf = config[analysis_type]
            
            # 1. Select the specific dimension value (Drill-down)
            dims = db.execute(f"SELECT {conf['id']}, name FROM {conf['table']} WHERE user_id = ?", [user_id]).fetchall()
            if not dims:
                print(f"No {conf['label'].lower()}s found.")
                return
                
            print(f"\nSelect {conf['label']}:")
            for i, d in enumerate(dims, 1):
                print(f"{i}. {d[1]}")
                
            selected_id = None
            selected_name = ""
            while True:
                try:
                    choice_idx = int(input(f"Enter {conf['label'].lower()} number: "))
                    if 1 <= choice_idx <= len(dims):
                        selected_id = dims[choice_idx-1][0]
                        selected_name = dims[choice_idx-1][1]
                        break
                    print("Invalid choice.")
                except ValueError:
                    print("Invalid input.")

            # 2. Query items for selected dimension
            # We need to join Categories, Colors, Brands to get names for the columns
            results = db.execute(f"""
                SELECT 
                    i.name as item_name,
                    cat.name as category_name,
                    c.name as color_name,
                    b.name as brand_name,
                    s.name as size_name,
                    COUNT(w.wear_id) as wear_count
                FROM Clothing_Items i
                LEFT JOIN Wear_Logs w ON i.item_id = w.item_id
                LEFT JOIN Categories cat ON i.category_id = cat.category_id
                LEFT JOIN Colors c ON i.color_id = c.color_id
                LEFT JOIN Brands b ON i.brand_id = b.brand_id
                LEFT JOIN Sizes s ON i.size_id = s.size_id
                WHERE i.user_id = ? AND i.{conf['id']} = ?
                GROUP BY i.item_id, i.name, cat.name, c.name, b.name, s.name
                ORDER BY wear_count DESC
            """, [user_id, selected_id]).fetchall()

            if not results:
                print(f"No items found for {conf['label']}: {selected_name}.")
                return

            print(f"\nWear counts for {conf['label']}: {selected_name}")
            
            # Prepare Header
            # Columns map to result indices: 0:Name, 1:Cat, 2:Color, 3:Brand, 4:Size, 5:Count
            # We construct the table based on conf['cols']
            
            # Mapping col name to (header_text, width, result_index)
            col_def = {
                'Item Name': ('Item Name', 20, 0),
                'Category': ('Category', 15, 1),
                'Color': ('Color', 10, 2),
                'Brand': ('Brand', 10, 3),
                'Size': ('Size', 8, 4),
                'Wear Count': ('Wear Count', 10, 5)
            }
            
            headers = ["#  "]
            widths = [3]
            indices = []
            
            for col_name in conf['cols']:
                h_text, width, idx = col_def[col_name]
                headers.append(f"{h_text:<{width}}")
                widths.append(width)
                indices.append(idx)
                
            header_str = " | ".join(headers)
            print("\n" + header_str)
            print("-" * len(header_str))
            
            plot_data = []
            for i, row in enumerate(results, 1):
                row_parts = [f"{i:<3}"]
                
                # Fetch data for each column
                for idx, width in zip(indices, widths[1:]): # skip # width
                    val = row[idx]
                    if val is None: val = "N/A"
                    if isinstance(val, int): val = str(val)
                    # Truncate if too long
                    if len(val) > width:
                        val = val[:width-2] + ".."
                    row_parts.append(f"{val:<{width}}")
                
                print(" | ".join(row_parts))
                plot_data.append((row[0], row[5])) # Name, Count

            if plot_data:
                names = [x[0] for x in plot_data]
                counts = [x[1] for x in plot_data]
                
                plt.figure(figsize=(12, 6))
                plt.bar(names, counts, color='lightgreen')
                plt.title(f'Wear Counts - {selected_name}')
                plt.xlabel('Item')
                plt.ylabel('Wear Count')
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                plt.show()
        
        else:
            print("Invalid choice.")
                
    except Exception as e:
        print(f"Error during analysis: {e}")

def wardrobe_composition_analytics(db, user_id):
    print("\nAnalyze by:")
    print("0. Back to Main Menu")
    print("1. Category distribution")
    print("2. Color distribution")
    print("3. Size distribution")
    print("4. Brand distribution")
    
    analysis_type = input("\nEnter your choice: ")
    
    try:
        if analysis_type == '0':
            return
        if analysis_type in ['1', '2', '3', '4']:
            config = {
                '1': {'table': 'Categories', 'id': 'category_id', 'label': 'Category',
                      'cols': ['Item Name', 'Color', 'Brand']},
                '2': {'table': 'Colors', 'id': 'color_id', 'label': 'Color',
                      'cols': ['Item Name', 'Category', 'Brand']},
                '3': {'table': 'Sizes', 'id': 'size_id', 'label': 'Size',
                      'cols': ['Item Name', 'Category', 'Color', 'Brand']},
                '4': {'table': 'Brands', 'id': 'brand_id', 'label': 'Brand',
                      'cols': ['Item Name', 'Category', 'Color']}
            }
            
            conf = config[analysis_type]
            table = conf['table']
            id_col = conf['id']
            
            # Query to get items with their dimension info
            # We join all dimensions to get names for columns
            query = f"""
                SELECT 
                    d.name as dimension_name,
                    i.name as item_name,
                    cat.name as category_name,
                    c.name as color_name,
                    b.name as brand_name,
                    s.name as size_name,
                    COUNT(i.item_id) OVER (PARTITION BY d.{id_col}) as group_count,
                    COUNT(i.item_id) OVER () as total_count
                FROM {table} d
                JOIN Clothing_Items i ON d.{id_col} = i.{id_col}
                LEFT JOIN Categories cat ON i.category_id = cat.category_id
                LEFT JOIN Colors c ON i.color_id = c.color_id
                LEFT JOIN Brands b ON i.brand_id = b.brand_id
                LEFT JOIN Sizes s ON i.size_id = s.size_id
                WHERE i.user_id = ?
                ORDER BY group_count DESC, dimension_name, item_name
            """
            
            results = db.execute(query, [user_id]).fetchall()
            
            if not results:
                print(f"\nNo items found for {conf['label']} analysis.")
                return

            print(f"\nWardrobe Composition by {conf['label']}:")
            
            # Column definitions: (Header, Width, Index in Query Result)
            col_def = {
                'Item Name': ('Item Name', 20, 1),
                'Category': ('Category', 15, 2),
                'Color': ('Color', 10, 3),
                'Brand': ('Brand', 10, 4),
                'Size': ('Size', 8, 5)
            }

            current_group = None
            plot_data = {}
            group_items_counter = 0
            
            # Pre-calculate headers for the chosen columns
            headers = ["#  "]
            widths = [3]
            indices = []
            for col_name in conf['cols']:
                h_text, width, idx = col_def[col_name]
                headers.append(f"{h_text:<{width}}")
                widths.append(width)
                indices.append(idx)
            header_str = " | ".join(headers)
            divider_str = "-" * len(header_str)

            for row in results:
                dim_name = row[0]
                group_count = row[6]
                total_count = row[7]
                
                if current_group != dim_name:
                    current_group = dim_name
                    percentage = (group_count / total_count) * 100
                    print(f"\n{dim_name} - total - {group_count} items ({percentage:.1f}%)")
                    
                    # Print Table Header for the new group
                    print(header_str)
                    print(divider_str)
                    
                    plot_data[dim_name] = group_count
                    group_items_counter = 0 # Reset counter for the new group
                
                group_items_counter += 1
                row_parts = [f"{group_items_counter:<3}"]
                
                for idx, width in zip(indices, widths[1:]):
                    val = row[idx]
                    if val is None: val = "N/A"
                    if len(val) > width:
                        val = val[:width-2] + ".."
                    row_parts.append(f"{val:<{width}}")
                
                print(" | ".join(row_parts))

            # Plotting
            if plot_data:
                sorted_plot = sorted(plot_data.items(), key=lambda x: x[1], reverse=True)
                names = [x[0] for x in sorted_plot]
                counts = [x[1] for x in sorted_plot]
                
                plt.figure(figsize=(10, 6))
                plt.bar(names, counts, color='skyblue')
                plt.title(f'Wardrobe Composition by {conf["label"]}')
                plt.xlabel(conf['label'])
                plt.ylabel('Item Count')
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                plt.show()
        
        else:
            print("Invalid choice.")
                        
    except Exception as e:
        print(f"Error during analysis: {e}")

def investment_analytics(db, user_id):
    print("\nAnalyze by:")
    print("0. Back to Main Menu")
    print("1. Cost per wear by category")
    print("2. Cost per wear by color")
    print("3. Cost per wear by brand")
    print("4. Monthly expenses through year")
    print("5. Daily expenses though month")
    
    choice = input("\nEnter your choice: ")
    
    try:
        if choice == '0':
            return
        if choice in ['1', '2', '3']:
            config = {
                '1': {'table': 'Categories', 'id': 'category_id', 'label': 'Category'},
                '2': {'table': 'Colors', 'id': 'color_id', 'label': 'Color'},
                '3': {'table': 'Brands', 'id': 'brand_id', 'label': 'Brand'}
            }
            conf = config[choice]
            
            # Get dimensions
            dims = db.execute(f"SELECT {conf['id']}, name FROM {conf['table']} WHERE user_id = ?", [user_id]).fetchall()
            if not dims:
                print(f"No {conf['label'].lower()}s found.")
                return
                
            print(f"\nSelect {conf['label']}:")
            for i, d in enumerate(dims, 1):
                print(f"{i}. {d[1]}")
                
            try:
                sub_choice = int(input("Enter number: "))
                if 1 <= sub_choice <= len(dims):
                    selected_id = dims[sub_choice-1][0]
                    selected_name = dims[sub_choice-1][1]
                    
                    # Get items and CPW
                    items = db.execute(f"""
                        SELECT 
                            i.name,
                            i.price,
                            COUNT(w.wear_id) as wear_count,
                            i.purchase_date
                        FROM Clothing_Items i
                        LEFT JOIN Wear_Logs w ON i.item_id = w.item_id
                        WHERE i.user_id = ? AND i.{conf['id']} = ?
                        GROUP BY i.item_id, i.name, i.price, i.purchase_date
                    """, [user_id, selected_id]).fetchall()
                    
                    if not items:
                        print(f"No items found in {selected_name}.")
                        return
                        
                    # Calculate CPW and sort
                    processed_items = []
                    for item in items:
                        name = item[0]
                        price = float(item[1]) if item[1] else 0.0
                        wears = item[2]
                        purchase_date = item[3]
                        
                        if wears > 0:
                            cpw = price / wears
                        else:
                            cpw = float('inf') # Infinite cost if never worn
                            
                        # Calculate Duration
                        duration_str = "N/A"
                        if purchase_date:
                            try:
                                if isinstance(purchase_date, str):
                                    p_date = datetime.strptime(purchase_date, '%Y-%m-%d').date()
                                else:
                                    p_date = purchase_date
                                
                                now = datetime.now().date()
                                total_months = (now.year - p_date.year) * 12 + (now.month - p_date.month)
                                if now.day < p_date.day:
                                    total_months -= 1
                                
                                if total_months < 0: total_months = 0
                                
                                if total_months == 0:
                                    days = (now - p_date).days
                                    duration_str = f"{days} days"
                                elif total_months < 12:
                                    duration_str = f"{total_months} months"
                                else:
                                    years = total_months // 12
                                    months = total_months % 12
                                    duration_str = f"{years} yrs {months} mos"
                            except Exception:
                                pass

                        processed_items.append({
                            'name': name, 'price': price, 'wears': wears, 
                            'cpw': cpw, 'duration': duration_str
                        })
                    
                    # Sort by CPW ascending (cheapest per wear first), then by price
                    processed_items.sort(key=lambda x: (x['cpw'], x['price']))
                    
                    print(f"\nCost Per Wear (CPW) for {selected_name}:")
                    print(f"{{:<20}} | {{:<10}} | {{:<6}} | {{:<10}} | {{:<18}}".format('Item', 'Price', 'Wears', 'CPW', 'Duration'))
                    print("-" * 75)
                    
                    for item in processed_items:
                        if item['cpw'] == float('inf'):
                            cpw_str = "No wears"
                        else:
                            cpw_str = f"${item['cpw']:.2f}"
                        
                        print(f"{{:<20}} | ${{:<9.2f}} | {{:<6}} | {{:<10}} | {{:<18}}".format(
                            item['name'][:20], item['price'], item['wears'], cpw_str, item['duration']))
                    
                    # Chart removed as requested
                else:
                    print("Invalid selection.")
            except ValueError:
                print("Invalid input.")

        elif choice == '4':
            current_year = datetime.now().year
            print("\nSelect Year:")
            print(f"1. {current_year}")
            print(f"2. {current_year - 1}")
            print(f"3. {current_year - 2}")
            
            y_choice = input("Enter choice: ")
            target_year = current_year
            
            if y_choice == '2': target_year -= 1
            elif y_choice == '3': target_year -= 2
            elif y_choice != '1': 
                print("Invalid choice")
                return
                
            results = db.execute("""
                SELECT 
                    strftime('%m', i.purchase_date) as month,
                    i.purchase_date,
                    i.name,
                    c.name,
                    b.name,
                    i.price
                FROM Clothing_Items i
                LEFT JOIN Colors c ON i.color_id = c.color_id
                LEFT JOIN Brands b ON i.brand_id = b.brand_id
                WHERE i.user_id = ? AND strftime('%Y', i.purchase_date) = ?
                ORDER BY i.purchase_date
            """, [user_id, str(target_year)]).fetchall()
            
            # Organize data by month
            months_data = {f"{m:02d}": {'total': 0.0, 'items': []} for m in range(1, 13)}
            
            for row in results:
                month = row[0]
                p_date = row[1]
                name = row[2]
                color = row[3] if row[3] else "N/A"
                brand = row[4] if row[4] else "N/A"
                price = float(row[5]) if row[5] is not None else None
                
                if month in months_data:
                    months_data[month]['total'] += (price if price else 0.0)
                    months_data[month]['items'].append({
                        'date': p_date, 'name': name, 'color': color, 
                        'brand': brand, 'price': price
                    })
            
            month_names = [datetime(2000, m, 1).strftime('%B') for m in range(1, 13)]
            amounts = [months_data[f"{m:02d}"]['total'] for m in range(1, 13)]
            
            print(f"\nMonthly Expenses for {target_year}:")
            
            # Header definition
            header = f"{'#':<3} | {'Date':<12} | {'Item Name':<20} | {'Color':<10} | {'Brand':<10} | {'Price':<10}"
            divider = "-" * len(header)

            for i, m_name in enumerate(month_names):
                month_key = f"{i+1:02d}"
                data = months_data[month_key]
                if data['total'] > 0:
                    print(f"\n{m_name}: Total ${data['total']:.2f}")
                    print(header)
                    print(divider)
                    for idx, item in enumerate(data['items'], 1):
                        date_val = str(item['date']) if item['date'] else "N/A"
                        name_val = item['name']
                        if len(name_val) > 20:
                            name_val = name_val[:17] + ".."
                        
                        color_val = str(item['color'])
                        brand_val = str(item['brand'])
                        
                        if item['price'] is not None:
                            price_val = f"${item['price']:.2f}"
                        else:
                            price_val = "N/A"
                            
                        print(f"{idx:<3} | {date_val:<12} | {name_val:<20} | {color_val:<10} | {brand_val:<10} | {price_val:<10}")
                
            plt.figure(figsize=(12, 6))
            plt.bar(month_names, amounts, color='skyblue')
            plt.title(f'Monthly Expenses - {target_year}')
            plt.ylabel('Amount ($)')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()

        elif choice == '5':
            now = datetime.now()
            print("\nSelect Month:")
            months_map = {}
            for m in range(1, now.month + 1):
                m_name = datetime(now.year, m, 1).strftime('%B')
                print(f"{m}. {m_name}")
                months_map[str(m)] = m
                
            m_choice = input("Enter choice: ")
            if m_choice in months_map:
                target_month = months_map[m_choice]
                target_month_str = f"{target_month:02d}"
                target_year_str = str(now.year)
                
                # Get number of days in the month
                _, num_days = calendar.monthrange(int(target_year_str), target_month)
                
                results = db.execute("""
                    SELECT 
                        strftime('%d', i.purchase_date) as day,
                        i.purchase_date,
                        i.name,
                        c.name,
                        b.name,
                        i.price
                    FROM Clothing_Items i
                    LEFT JOIN Colors c ON i.color_id = c.color_id
                    LEFT JOIN Brands b ON i.brand_id = b.brand_id
                    WHERE i.user_id = ? 
                    AND strftime('%Y', i.purchase_date) = ?
                    AND strftime('%m', i.purchase_date) = ?
                    ORDER BY i.purchase_date
                """, [user_id, target_year_str, target_month_str]).fetchall()
                
                # Initialize data for all days in the month
                daily_data = {f"{d:02d}": {'total': 0.0, 'items': []} for d in range(1, num_days + 1)}
                
                for row in results:
                    day = row[0]
                    p_date = row[1]
                    name = row[2]
                    color = row[3] if row[3] else "N/A"
                    brand = row[4] if row[4] else "N/A"
                    price = float(row[5]) if row[5] is not None else None
                    
                    if day in daily_data:
                        daily_data[day]['total'] += (price if price else 0.0)
                        daily_data[day]['items'].append({
                            'date': p_date, 'name': name, 'color': color, 
                            'brand': brand, 'price': price
                        })
                
                # Prepare plot data with ALL days
                days = sorted(daily_data.keys())
                amounts = [daily_data[d]['total'] for d in days]
                
                print(f"\nDaily Expenses for {datetime(now.year, target_month, 1).strftime('%B')} {target_year_str}:")
                
                # Header definition
                header = f"{'#':<3} | {'Date':<12} | {'Item Name':<20} | {'Color':<10} | {'Brand':<10} | {'Price':<10}"
                divider = "-" * len(header)
                
                has_data = False
                for day in days:
                    data = daily_data[day]
                    if data['total'] > 0:
                        has_data = True
                        print(f"\nDay {day}: Total ${data['total']:.2f}")
                        print(header)
                        print(divider)
                        for idx, item in enumerate(data['items'], 1):
                            date_val = str(item['date']) if item['date'] else "N/A"
                            name_val = item['name']
                            if len(name_val) > 20:
                                name_val = name_val[:17] + ".."
                            
                            color_val = str(item['color'])
                            brand_val = str(item['brand'])
                            
                            if item['price'] is not None:
                                price_val = f"${item['price']:.2f}"
                            else:
                                price_val = "N/A"
                                
                            print(f"{idx:<3} | {date_val:<12} | {name_val:<20} | {color_val:<10} | {brand_val:<10} | {price_val:<10}")
                
                if not has_data:
                    print("No expenses found for this month.")
                    
                plt.figure(figsize=(12, 6))
                plt.bar(days, amounts, color='lightgreen')
                plt.title(f'Daily Expenses - {datetime(now.year, target_month, 1).strftime("%B")} {target_year_str}')
                plt.xlabel('Day')
                plt.ylabel('Amount ($)')
                plt.tight_layout()
                plt.show()
            else:
                print("Invalid month.")
        
        else:
            print("Invalid choice.")

    except ValueError:
        print("Invalid input.")
    except Exception as e:
        print(f"Error during analysis: {e}")