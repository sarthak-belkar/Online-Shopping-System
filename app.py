from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3

app = Flask(__name__)

app.secret_key = 'your_secret_key'

# Create the database if not exists
def init_db():
    conn = sqlite3.connect('mydatabase.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        email TEXT UNIQUE,
        phone TEXT,
        password TEXT
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        description TEXT,
        image_url TEXT,
        category TEXT
    )''')
    
    # Insert sample products if the table is empty
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        sample_products = [
            ("Wireless Earbuds", 79.99, "High-quality wireless earbuds with noise cancellation", "static/images/51pycg0MGxL.jpg", "Electronics"),
        ]
        cursor.executemany("INSERT INTO products (name, price, description, image_url, category) VALUES (?, ?, ?, ?, ?)", sample_products)
    
    conn.commit()
    conn.close()

init_db()

@app.route('/', methods=['GET'])
def index():
    return render_template('login.html')

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/api/products')
def get_products():
    conn = sqlite3.connect('mydatabase.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products ORDER BY RANDOM() LIMIT 8")
    products = cursor.fetchall()
    conn.close()
    
    # Convert products to list of dictionaries
    products_list = []
    for product in products:
        products_list.append({
            'id': product[0],
            'name': product[1],
            'price': product[2],
            'description': product[3],
            'image_url': product[4],
            'category': product[5]
        })
    
    return jsonify(products_list)

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    email = request.form['email']
    phone = request.form['phone']
    password = request.form['password']

    conn = sqlite3.connect('mydatabase.db')
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO users (username, email, phone, password) VALUES (?, ?, ?, ?)",
                       (username, email, phone, password))
        conn.commit()
        flash("Signup successful! Please log in.")
    except sqlite3.IntegrityError:
        flash("Email already exists. Try a different one.")
    conn.close()

    return redirect(url_for('index'))


@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    conn = sqlite3.connect('mydatabase.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        return render_template('index.html') # user[1] = username
    else:
        return "Invalid credentials"

if __name__ == '__main__':
    app.run(debug=True)
