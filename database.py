import sqlite3

conn = sqlite3.connect("shop.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    price TEXT,
    description TEXT,
    image TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS cart (
    user_id INTEGER,
    product_id INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    products TEXT,
    phone TEXT,
    address TEXT,
    status TEXT DEFAULT 'NEW'
)
""")

conn.commit()

def add_product(name, price, description, image):

    cursor.execute("""
    INSERT INTO products (name, price, description, image)
    VALUES (?, ?, ?, ?)
    """, (name, price, description, image))

    conn.commit()

def get_products():

    cursor.execute("SELECT * FROM products")
    return cursor.fetchall()

def get_cart(user_id):

    cursor.execute("""
    SELECT products.id, products.name, products.price
    FROM cart
    JOIN products ON cart.product_id = products.id
    WHERE cart.user_id=?
    """, (user_id,))

    return cursor.fetchall()

def add_to_cart(user_id, product_id):

    cursor.execute("""
    INSERT INTO cart (user_id, product_id)
    VALUES (?, ?)
    """, (user_id, product_id))

    conn.commit()

def clear_cart(user_id):

    cursor.execute("DELETE FROM cart WHERE user_id=?", (user_id,))
    conn.commit()

def create_order(user_id, products, phone, address):

    cursor.execute("""
    INSERT INTO orders (user_id, products, phone, address)
    VALUES (?, ?, ?, ?)
    """, (user_id, products, phone, address))

    conn.commit()
