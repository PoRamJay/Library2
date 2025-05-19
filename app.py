from flask import Flask, render_template, redirect, url_for, session, request, flash
import os
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder='templates')
app.secret_key = 'your_secret_key'  # Needed for session

# Add a helper function for DB connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # Set your MySQL password if you have one
        database="library_db"  # Change to your actual database name
    )

@app.route('/')
def index():
    return redirect(url_for('signup'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            flash('Passwords do not match!')
            return render_template('signup.html')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE username = %s', (username,))
        if cursor.fetchone():
            flash('Username already exists!')
            cursor.close()
            conn.close()
            return render_template('signup.html')
        password_hash = generate_password_hash(password)
        cursor.execute('INSERT INTO users (username, password_hash) VALUES (%s, %s)', (username, password_hash))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Signup successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT password_hash FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user and check_password_hash(user[0], password):
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password!')
    return render_template('login.html')

@app.route('/loginadmin')
def loginadmin():
    return render_template('loginadmin.html')

# Simulate login for demonstration (no real authentication)
@app.route('/do_login')
def do_login():
    session['logged_in'] = True
    return redirect(url_for('home'))

@app.route('/home')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('Home Page - Lib.html')

@app.route('/library')
def library():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('Home Page - Lib.html')

@app.route('/add_items')
def add_items():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('add_items.html')

@app.route('/add_collection')
def add_collection():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('add_collection.html')

@app.route('/add_items_click')
def add_items_click():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('Items_click.html')

@app.route('/add_items_search')
def add_items_search():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('add search.html')

@app.route('/personal_collection')
def personal_collection():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('personal_collection.html')

@app.route('/collection_view')
def collection_view():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('collectionview.html')

if __name__ == '__main__':
    app.run(debug=True)
