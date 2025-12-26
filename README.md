# Smart Wardrobe Tracker (CLI Application)

A **Python-based command-line wardrobe management system** that allows users to **track clothing items, log wears, and generate powerful analytics** on wardrobe usage, spending, and wear efficiency.

This project focuses on **data-driven wardrobe insights,** composed of features for user management, wardrobe management, wear logging, and wear analytics. Core highlights are the advanced analytics showing **how often items are worn, how much they cost per wear, and how their wardrobe is composed** across categories, brands, colors, and time.

---

## Key Features

### User Management

- Secure user **registration & login**
- Email validation and password checks
- User-specific wardrobes and analytics

---

### Wardrobe Management

- Add, view, search, and remove clothing items
- Fully normalized attributes:
    - Categories
    - Colors
    - Sizes
    - Brands
- Track:
    - Purchase date
    - Price (optional)

---

### Wear Logging

- Log each time an item is worn
- View complete wear history
- Remove incorrect entries
- Advanced filtering by:
    - Item
    - Category
    - Color
    - Size
    - Brand
    - Date range

---

### Advanced Analytics

This system supports **rich, flexible analytics**, including:

- **Wear Count Analytics**
    - Per item
    - Per category
    - Per color
    - Per brand
- **Wardrobe Composition Analytics**
    - Breakdown of wardrobe by category, color, brand, and size
- **Investment Analytics**
    - Total spend per month
    - Spend per brand
    - Cost-per-wear analysis
    - Identify underused vs. high-value items

> Almost any analytical question about usage, cost, frequency, or composition can be answered along with visualizations. 
> 

---

## Technical Design

- **Language:** Python
- **Database:** DuckDB (SQL-based, embedded analytics database)
- **Architecture:** Modular design
    - `user_menu`
    - `item_management`
    - `wear_entry_management`
    - `analytics_management`
- **Data Model:** Fully relational schema with foreign keys
- **Interface:** Command-Line Interface (CLI)

---

## Database Schema

- `Users`
- `Categories`
- `Colors`
- `Sizes`
- `Brands`
- `Clothing_Items`
- `Wear_Logs`

Designed to support **efficient joins and flexible analytics queries**.
