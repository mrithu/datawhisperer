"""
DataWhisperer - Database Seeder
Creates a rich e-commerce SQLite database for demo purposes.
Run: python setup/seed_db.py
"""

import sqlite3
import random
from datetime import datetime, timedelta
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "ecommerce.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

CITIES = [
    ("Mumbai", "Maharashtra"), ("Delhi", "Delhi"), ("Bengaluru", "Karnataka"),
    ("Chennai", "Tamil Nadu"), ("Hyderabad", "Telangana"), ("Pune", "Maharashtra"),
    ("Kolkata", "West Bengal"), ("Ahmedabad", "Gujarat"), ("Jaipur", "Rajasthan"),
    ("Surat", "Gujarat"), ("Lucknow", "Uttar Pradesh"), ("Kochi", "Kerala"),
]

CATEGORIES = ["Electronics", "Apparel", "Home & Kitchen", "Books", "Beauty", "Sports", "Toys", "Grocery"]

PRODUCTS = [
    ("Wireless Earbuds Pro", "Electronics", 2999, 899),
    ("Smart Watch Series X", "Electronics", 8999, 3500),
    ("4K Webcam Ultra", "Electronics", 5499, 2200),
    ("Mechanical Keyboard RGB", "Electronics", 3499, 1400),
    ("Noise Cancelling Headphones", "Electronics", 6999, 2800),
    ("USB-C Hub 7-in-1", "Electronics", 1999, 750),
    ("Portable SSD 1TB", "Electronics", 4999, 2000),
    ("LED Desk Lamp Smart", "Electronics", 1499, 600),

    ("Premium Cotton T-Shirt", "Apparel", 799, 200),
    ("Denim Jacket Classic", "Apparel", 2499, 800),
    ("Yoga Pants Flex", "Apparel", 1299, 400),
    ("Running Shoes AirStep", "Apparel", 3999, 1600),
    ("Winter Hoodie Fleece", "Apparel", 1899, 600),
    ("Linen Formal Shirt", "Apparel", 1599, 500),

    ("Air Fryer 5L Digital", "Home & Kitchen", 4499, 1800),
    ("Stainless Steel Cookware Set", "Home & Kitchen", 3299, 1200),
    ("Bamboo Cutting Board Set", "Home & Kitchen", 899, 250),
    ("French Press Coffee Maker", "Home & Kitchen", 1299, 450),
    ("Robot Vacuum Cleaner", "Home & Kitchen", 12999, 5500),
    ("Instant Pot 6Qt", "Home & Kitchen", 6499, 2600),

    ("Python Mastery 2025", "Books", 599, 120),
    ("The Lean Startup", "Books", 449, 90),
    ("Atomic Habits", "Books", 399, 80),
    ("Deep Work", "Books", 349, 70),

    ("Vitamin C Serum 30ml", "Beauty", 699, 150),
    ("Hyaluronic Moisturiser", "Beauty", 899, 200),
    ("Charcoal Face Wash", "Beauty", 349, 80),
    ("Sunscreen SPF 50+", "Beauty", 499, 110),

    ("Yoga Mat Non-Slip", "Sports", 1299, 400),
    ("Resistance Bands Set", "Sports", 799, 180),
    ("Adjustable Dumbbells 20kg", "Sports", 5999, 2400),
    ("Jump Rope Speed", "Sports", 399, 80),

    ("LEGO Architecture Set", "Toys", 3499, 1400),
    ("Remote Control Car Pro", "Toys", 1999, 700),

    ("Organic Green Tea 200g", "Grocery", 449, 120),
    ("Cold Pressed Coconut Oil 1L", "Grocery", 599, 180),
    ("Mixed Nuts Premium 500g", "Grocery", 799, 300),
]

FIRST_NAMES = ["Aarav", "Priya", "Rahul", "Ananya", "Vikram", "Sneha", "Arjun", "Kavya",
               "Rohan", "Divya", "Kiran", "Meera", "Aditya", "Pooja", "Siddharth", "Nisha",
               "Amit", "Shruti", "Ravi", "Lakshmi", "Neha", "Suresh", "Deepa", "Ajay"]
LAST_NAMES = ["Sharma", "Patel", "Reddy", "Kumar", "Singh", "Nair", "Iyer", "Gupta",
              "Mehta", "Joshi", "Verma", "Rao", "Pillai", "Bose", "Das", "Shah"]

STATUSES = ["delivered", "delivered", "delivered", "shipped", "processing", "cancelled", "returned"]

def seed():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Drop and recreate tables
    c.executescript("""
        DROP TABLE IF EXISTS order_items;
        DROP TABLE IF EXISTS orders;
        DROP TABLE IF EXISTS products;
        DROP TABLE IF EXISTS customers;
        DROP TABLE IF EXISTS categories;

        CREATE TABLE categories (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT
        );

        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category_id INTEGER,
            price REAL NOT NULL,
            cost REAL NOT NULL,
            stock_qty INTEGER DEFAULT 0,
            rating REAL DEFAULT 4.0,
            review_count INTEGER DEFAULT 0,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        );

        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            city TEXT,
            state TEXT,
            joined_date TEXT,
            tier TEXT DEFAULT 'standard'
        );

        CREATE TABLE orders (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            order_date TEXT,
            status TEXT,
            shipping_city TEXT,
            shipping_state TEXT,
            total_amount REAL,
            payment_method TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        );

        CREATE TABLE order_items (
            id INTEGER PRIMARY KEY,
            order_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            unit_price REAL,
            discount_pct REAL DEFAULT 0,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        );
    """)

    # Seed categories
    cat_map = {}
    for i, cat in enumerate(CATEGORIES, 1):
        c.execute("INSERT INTO categories VALUES (?, ?, ?)", (i, cat, f"{cat} products"))
        cat_map[cat] = i

    # Seed products
    for i, (name, cat, price, cost) in enumerate(PRODUCTS, 1):
        stock = random.randint(10, 500)
        rating = round(random.uniform(3.5, 5.0), 1)
        reviews = random.randint(12, 4800)
        c.execute("INSERT INTO products VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                  (i, name, cat_map[cat], price, cost, stock, rating, reviews))

    # Seed customers (800 customers)
    tiers = ["standard", "standard", "standard", "silver", "gold", "platinum"]
    payment_methods = ["UPI", "Credit Card", "Debit Card", "Net Banking", "Cash on Delivery", "Wallet"]
    customer_cities = []
    for i in range(1, 801):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        name = f"{first} {last}"
        email = f"{first.lower()}.{last.lower()}{i}@example.com"
        city, state = random.choice(CITIES)
        joined = (datetime.now() - timedelta(days=random.randint(30, 900))).strftime("%Y-%m-%d")
        tier = random.choice(tiers)
        c.execute("INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (i, name, email, city, state, joined, tier))
        customer_cities.append((city, state))

    # Seed orders (3500 orders over last 18 months)
    order_id = 1
    item_id = 1
    for _ in range(3500):
        cust_id = random.randint(1, 800)
        city, state = customer_cities[cust_id - 1]
        days_ago = random.randint(1, 540)
        order_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        status = random.choice(STATUSES)
        payment = random.choice(payment_methods)

        # Each order has 1-4 items
        n_items = random.randint(1, 4)
        chosen_products = random.sample(range(1, len(PRODUCTS) + 1), min(n_items, len(PRODUCTS)))

        total = 0
        items_data = []
        for prod_id in chosen_products:
            prod = PRODUCTS[prod_id - 1]
            qty = random.randint(1, 3)
            price = prod[2]
            discount = random.choice([0, 0, 0, 5, 10, 15, 20])
            line_total = qty * price * (1 - discount / 100)
            total += line_total
            items_data.append((item_id, order_id, prod_id, qty, price, discount))
            item_id += 1

        c.execute("INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                  (order_id, cust_id, order_date, status, city, state, round(total, 2), payment))

        for item in items_data:
            c.execute("INSERT INTO order_items VALUES (?, ?, ?, ?, ?, ?)", item)

        order_id += 1

    conn.commit()
    conn.close()
    print(f"✅ Database seeded at: {DB_PATH}")
    print(f"   → {len(PRODUCTS)} products across {len(CATEGORIES)} categories")
    print(f"   → 800 customers across {len(CITIES)} cities")
    print(f"   → 3,500 orders with line items")

if __name__ == "__main__":
    seed()
