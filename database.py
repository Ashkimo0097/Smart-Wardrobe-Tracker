import duckdb

# Initialize database connection
db = duckdb.connect(database='wardrobe.db', read_only=False)

def create_tables():
    # Create tables if they don't exist
    db.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            user_id INTEGER PRIMARY KEY,
            name VARCHAR NOT NULL,
            email VARCHAR UNIQUE NOT NULL,
            password VARCHAR NOT NULL
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS Categories (
            category_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            name VARCHAR NOT NULL,
            FOREIGN KEY (user_id) REFERENCES Users(user_id)
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS Colors (
            color_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            name VARCHAR NOT NULL,
            FOREIGN KEY (user_id) REFERENCES Users(user_id)
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS Sizes (
            size_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            name VARCHAR NOT NULL,
            FOREIGN KEY (user_id) REFERENCES Users(user_id)
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS Brands (
            brand_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            name VARCHAR NOT NULL,
            FOREIGN KEY (user_id) REFERENCES Users(user_id)
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS Clothing_Items (
            item_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            name VARCHAR NOT NULL,
            category_id INTEGER,
            color_id INTEGER,
            size_id INTEGER,
            brand_id INTEGER,
            purchase_date DATE,
            price DECIMAL(10,2),
            FOREIGN KEY (user_id) REFERENCES Users(user_id),
            FOREIGN KEY (category_id) REFERENCES Categories(category_id),
            FOREIGN KEY (color_id) REFERENCES Colors(color_id),
            FOREIGN KEY (size_id) REFERENCES Sizes(size_id),
            FOREIGN KEY (brand_id) REFERENCES Brands(brand_id)
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS Wear_Logs (
            wear_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            item_id INTEGER,
            wear_date DATE NOT NULL,
            FOREIGN KEY (user_id) REFERENCES Users(user_id),
            FOREIGN KEY (item_id) REFERENCES Clothing_Items(item_id)
        )
    """)