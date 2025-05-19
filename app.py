from flask import Flask, render_template, redirect, url_for, session, request, flash
import os
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import uuid, datetime

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
    if session.get('logged_in'):
        if session.get('user_type') == 'admin':
            return redirect(url_for('adminlibrary'))
        else:
            return redirect(url_for('library'))
    return redirect(url_for('signup'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        user_type = request.form.get('user_type', 'user')
        if password != confirm_password:
            flash('Passwords do not match!')
            return render_template('signup.html')
        conn = get_db_connection()
        cursor = conn.cursor()
        if user_type == 'admin':
            cursor.execute('SELECT id FROM admins WHERE username = %s', (username,))
        else:
            cursor.execute('SELECT id FROM users WHERE username = %s', (username,))
        if cursor.fetchone():
            flash('Username already exists!')
            cursor.close()
            conn.close()
            return render_template('signup.html')
        password_hash = generate_password_hash(password)
        if user_type == 'admin':
            cursor.execute('INSERT INTO admins (username, password_hash) VALUES (%s, %s)', (username, password_hash))
        else:
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
        user_type = request.form.get('user_type', 'user')
        conn = get_db_connection()
        cursor = conn.cursor()
        if user_type == 'user':
            cursor.execute('SELECT password_hash FROM users WHERE username = %s', (username,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            if user and check_password_hash(user[0], password):
                session['logged_in'] = True
                session['username'] = username
                session['user_type'] = 'user'
                return redirect(url_for('home'))
            else:
                flash('Invalid username or password!')
        elif user_type == 'admin':
            cursor.execute('SELECT password_hash FROM admins WHERE username = %s', (username,))
            admin = cursor.fetchone()
            cursor.close()
            conn.close()
            if admin and check_password_hash(admin[0], password):
                session['logged_in'] = True
                session['username'] = username
                session['user_type'] = 'admin'
                return redirect(url_for('bookcatalog'))
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
    if session.get('user_type') == 'admin':
        return redirect(url_for('adminlibrary'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    # Get user's collections
    cursor.execute('''
        SELECT c.*, COUNT(cb.book_id) as book_count 
        FROM collections c 
        LEFT JOIN collection_books cb ON c.id = cb.collection_id 
        WHERE c.user_id = (SELECT id FROM users WHERE username = %s) 
        GROUP BY c.id
    ''', (session['username'],))
    collections = cursor.fetchall()
    # Get all books from all collections for this user
    books = []
    if collections:
        cursor.execute('''
            SELECT DISTINCT b.*, c.name as collection_name 
            FROM books b 
            JOIN collection_books cb ON b.id = cb.book_id 
            JOIN collections c ON cb.collection_id = c.id 
            WHERE c.user_id = (SELECT id FROM users WHERE username = %s)
            ORDER BY b.title
        ''', (session['username'],))
        books = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('Home Page - Lib.html', collections=collections, books=books)

@app.route('/library')
def library():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    search = request.args.get('search', '').strip()
    sort = request.args.get('sort', 'az')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Build the base query
    query = '''
        SELECT c.*, COUNT(cb.book_id) as book_count 
        FROM collections c 
        LEFT JOIN collection_books cb ON c.id = cb.collection_id 
        WHERE c.user_id = (SELECT id FROM users WHERE username = %s)
    '''
    params = [session['username']]

    # Add search filter
    if search:
        query += " AND LOWER(c.name) LIKE %s"
        params.append(f"%{search.lower()}%")

    query += " GROUP BY c.id"

    # Add sort
    if sort == 'za':
        query += " ORDER BY c.name DESC"
    else:
        query += " ORDER BY c.name ASC"

    cursor.execute(query, params)
    collections = cursor.fetchall()

    # Get all books from all collections for this user
    books = []
    if collections:
        cursor.execute('''
            SELECT DISTINCT b.*, c.name as collection_name 
            FROM books b 
            JOIN collection_books cb ON b.id = cb.book_id 
            JOIN collections c ON cb.collection_id = c.id 
            WHERE c.user_id = (SELECT id FROM users WHERE username = %s)
            ORDER BY b.title
        ''', (session['username'],))
        books = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('Home Page - Lib.html', 
                         collections=collections,
                         books=books)

@app.route('/add_items', methods=['GET', 'POST'])
def add_items():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    search = request.args.get('search', '').strip()
    sort = request.args.get('sort', 'az')
    message = None
    search_results = None

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        collection_id = request.form.get('collection_id')
        search_query = request.form.get('search_query', '').strip()
        search_type = request.form.get('search_type', 'keyword')
        book_id = request.form.get('book_id')
        username = session.get('username')

        if collection_id:
            cursor.execute('SELECT id FROM collections WHERE id = %s', (collection_id,))
            if not cursor.fetchone():
                message = "Selected collection does not exist. Please select a valid collection."
            else:
                if book_id:
                    cursor.execute('SELECT * FROM books WHERE id = %s', (book_id,))
                    book = cursor.fetchone()
                    if book:
                        if book.get('status', 'available') == 'borrowed':
                            message = f"Book '{book['title']}' is currently borrowed."
                        else:
                            cursor.execute('SELECT * FROM collection_books WHERE collection_id = %s AND book_id = %s', (collection_id, book['id']))
                            if not cursor.fetchone():
                                cursor.execute('INSERT INTO collection_books (collection_id, book_id) VALUES (%s, %s)', (collection_id, book['id']))
                                cursor.execute('UPDATE books SET status = %s WHERE id = %s', ('borrowed', book['id']))
                                # Add to booklog (correct table/columns)
                                transaction_id = str(uuid.uuid4().int)[:15]
                                today = datetime.date.today()
                                return_date = today + datetime.timedelta(days=14)
                                cursor.execute('INSERT INTO booklog (book_id, borrower_name, borrower_date, returner_date, status, transaction_id) VALUES (%s, %s, %s, %s, %s, %s)',
                                    (book['id'], username, today, return_date, 'Borrowed', transaction_id))
                                conn.commit()
                                message = f"Book '{book['title']}' added to collection and marked as borrowed!"
                            else:
                                message = f"Book '{book['title']}' is already in this collection."
                elif search_query:
                    if search_type == 'isbn':
                        cursor.execute('SELECT * FROM books WHERE CAST(isbn AS CHAR) = %s', (search_query,))
                        book = cursor.fetchone()
                        if book:
                            if book.get('status', 'available') == 'borrowed':
                                message = f"Book '{book['title']}' is currently borrowed."
                            else:
                                cursor.execute('SELECT * FROM collection_books WHERE collection_id = %s AND book_id = %s', (collection_id, book['id']))
                                if not cursor.fetchone():
                                    cursor.execute('INSERT INTO collection_books (collection_id, book_id) VALUES (%s, %s)', (collection_id, book['id']))
                                    cursor.execute('UPDATE books SET status = %s WHERE id = %s', ('borrowed', book['id']))
                                    # Add to booklog (correct table/columns)
                                    transaction_id = str(uuid.uuid4().int)[:15]
                                    today = datetime.date.today()
                                    return_date = today + datetime.timedelta(days=14)
                                    cursor.execute('INSERT INTO booklog (book_id, borrower_name, borrower_date, returner_date, status, transaction_id) VALUES (%s, %s, %s, %s, %s, %s)',
                                        (book['id'], username, today, return_date, 'Borrowed', transaction_id))
                                    conn.commit()
                                    message = f"Book '{book['title']}' added to collection and marked as borrowed!"
                                else:
                                    message = f"Book '{book['title']}' is already in this collection."
                            search_results = [book]
                        else:
                            message = "No book found with that ISBN."
                    else:
                        cursor.execute('''
                            SELECT * FROM books 
                            WHERE LOWER(title) LIKE %s 
                            OR LOWER(author) LIKE %s 
                            OR LOWER(genre) LIKE %s
                            LIMIT 1
                        ''', (f'%{search_query.lower()}%', f'%{search_query.lower()}%', f'%{search_query.lower()}%'))
                        book = cursor.fetchone()
                        if book:
                            if book.get('status', 'available') == 'borrowed':
                                message = f"Book '{book['title']}' is currently borrowed."
                            else:
                                cursor.execute('SELECT * FROM collection_books WHERE collection_id = %s AND book_id = %s', (collection_id, book['id']))
                                if not cursor.fetchone():
                                    cursor.execute('INSERT INTO collection_books (collection_id, book_id) VALUES (%s, %s)', (collection_id, book['id']))
                                    cursor.execute('UPDATE books SET status = %s WHERE id = %s', ('borrowed', book['id']))
                                    # Add to booklog (correct table/columns)
                                    transaction_id = str(uuid.uuid4().int)[:15]
                                    today = datetime.date.today()
                                    return_date = today + datetime.timedelta(days=14)
                                    cursor.execute('INSERT INTO booklog (book_id, borrower_name, borrower_date, returner_date, status, transaction_id) VALUES (%s, %s, %s, %s, %s, %s)',
                                        (book['id'], username, today, return_date, 'Borrowed', transaction_id))
                                    conn.commit()
                                    message = f"Book '{book['title']}' added to collection and marked as borrowed!"
                                else:
                                    message = f"Book '{book['title']}' is already in this collection."
                            search_results = [book]
                        else:
                            message = "No books found matching your search."

    # Build the base query for books
    query = '''
        SELECT b.*, COUNT(cb.collection_id) as collection_count
        FROM books b
        LEFT JOIN collection_books cb ON b.id = cb.book_id
        WHERE 1=1
    '''
    params = []

    # Add search filter
    if search:
        query += " AND (LOWER(b.title) LIKE %s OR LOWER(b.author) LIKE %s OR b.isbn LIKE %s)"
        params.extend([f"%{search.lower()}%", f"%{search.lower()}%", f"%{search}%"])

    query += " GROUP BY b.id"

    # Add sort
    if sort == 'za':
        query += " ORDER BY b.title DESC"
    else:
        query += " ORDER BY b.title ASC"

    cursor.execute(query, params)
    books = cursor.fetchall()

    # Get user's collections
    cursor.execute('''
        SELECT c.* 
        FROM collections c 
        WHERE c.user_id = (SELECT id FROM users WHERE username = %s)
        ORDER BY c.name
    ''', (session['username'],))
    collections = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('add_items.html', 
                         collections=collections, 
                         books=books, 
                         message=message,
                         search_results=search_results)

@app.route('/add_collection', methods=['GET', 'POST'])
def add_collection():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    # --- Search and filter logic for GET requests ---
    search = request.args.get('search', '').strip()
    sort = request.args.get('sort', 'az')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Build the base query
    query = '''
        SELECT c.*, COUNT(cb.book_id) as book_count 
        FROM collections c 
        LEFT JOIN collection_books cb ON c.id = cb.collection_id 
        WHERE c.user_id = (SELECT id FROM users WHERE username = %s)
    '''
    params = [session['username']]

    # Add search filter
    if search:
        query += " AND LOWER(c.name) LIKE %s"
        params.append(f"%{search.lower()}%")

    query += " GROUP BY c.id"

    # Add sort
    if sort == 'za':
        query += " ORDER BY c.name DESC"
    else:
        query += " ORDER BY c.name ASC"

    cursor.execute(query, params)
    collections = cursor.fetchall()

    # --- Handle POST for adding a new collection ---
    if request.method == 'POST':
        collection_name = request.form['collection_name']
        language = request.form.get('language', 'en')  # Get language from form

        if not collection_name:
            flash('Collection name is required!')
            cursor.close()
            conn.close()
            return render_template('add_collection.html', collections=collections)

        # Get user_id from username in session
        cursor.execute('SELECT id FROM users WHERE username = %s', (session['username'],))
        user = cursor.fetchone()
        if not user:
            flash('User not found!')
            cursor.close()
            conn.close()
            return render_template('add_collection.html', collections=collections)

        user_id = user['id']
        cursor.execute('INSERT INTO collections (name, user_id, language) VALUES (%s, %s, %s)', 
                      (collection_name, user_id, language))
        conn.commit()
        flash('Collection added successfully!')
        # Refresh collections after adding
        cursor.execute(query, params)
        collections = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template('add_collection.html', collections=collections)

@app.route('/add_items_click', methods=['GET', 'POST'])
def add_items_click():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get user's collections
    cursor.execute('''
        SELECT c.* 
        FROM collections c 
        WHERE c.user_id = (SELECT id FROM users WHERE username = %s)
        ORDER BY c.name
    ''', (session['username'],))
    collections = cursor.fetchall()

    search_query = ''
    selected_collection = None
    message = None
    search_results = []

    if request.method == 'POST':
        collection_id = request.form.get('collection_id')
        search_query = request.form.get('search_query', '').strip()

        if collection_id and search_query:
            # Get the selected collection details
            cursor.execute('SELECT * FROM collections WHERE id = %s', (collection_id,))
            selected_collection = cursor.fetchone()

            # Try to find by ISBN (exact match, numeric or string)
            cursor.execute('SELECT * FROM books WHERE isbn = %s', (search_query,))
            book = cursor.fetchone()

            # If not found by ISBN, try by title (case-insensitive)
            if not book:
                cursor.execute('SELECT * FROM books WHERE LOWER(title) = %s', (search_query.lower(),))
                book = cursor.fetchone()

            if book:
                # Check if book already exists in collection
                cursor.execute('SELECT * FROM collection_books WHERE collection_id = %s AND book_id = %s',
                               (collection_id, book['id']))
                if not cursor.fetchone():
                    cursor.execute('INSERT INTO collection_books (collection_id, book_id) VALUES (%s, %s)',
                                   (collection_id, book['id']))
                    conn.commit()
                    message = f"Book '{book['title']}' added to collection!"
                else:
                    message = f"Book '{book['title']}' is already in this collection."
                search_results = [book]
            else:
                message = "No book found with that ISBN or title."

    cursor.close()
    conn.close()

    return render_template(
        'Items_click.html',
        collections=collections,
        selected_collection=selected_collection,
        search_query=search_query,
        search_results=search_results,
        message=message
    )

@app.route('/add_items_search')
def add_items_search():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('add search.html')

@app.route('/personal_collection')
def personal_collection():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return redirect(url_for('library'))  # Redirect to library for consistent layout

@app.route('/collection_view')
def collection_view():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    collection_id = request.args.get('id')
    if not collection_id:
        return redirect(url_for('library'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get the collection
    cursor.execute('SELECT * FROM collections WHERE id = %s', (collection_id,))
    collection = cursor.fetchone()
    if not collection:
        cursor.close()
        conn.close()
        return redirect(url_for('library'))

    # Get books in this collection
    cursor.execute('''
        SELECT b.*
        FROM books b
        JOIN collection_books cb ON b.id = cb.book_id
        WHERE cb.collection_id = %s
        ORDER BY b.title
    ''', (collection_id,))
    books = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('collectionview.html', collection=collection, books=books)

@app.route('/support')
def support():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if session.get('user_type') == 'admin':
        return render_template('support_admin.html')
    return render_template('support.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/booklog')
def booklog():
    if not session.get('logged_in') or session.get('user_type') != 'admin':
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT b.title AS book_title, b.author AS book_author, l.borrower_name, l.borrower_date, l.returner_date, l.status, l.transaction_id
        FROM booklog l
        JOIN books b ON l.book_id = b.id
        ORDER BY l.borrower_date DESC
    ''')
    logs = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('booklog.html', logs=logs)

@app.route('/adminlibrary')
def adminlibrary():
    if not session.get('logged_in') or session.get('user_type') != 'admin':
        return redirect(url_for('login'))
    return render_template('adminlibrary.html')

@app.route('/borrowerprofile')
def borrowerprofile():
    if not session.get('logged_in') or session.get('user_type') != 'admin':
        return redirect(url_for('login'))
    search = request.args.get('search', '').strip()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if search:
        cursor.execute('SELECT id, username FROM users WHERE LOWER(username) LIKE %s', (f"%{search.lower()}%",))
    else:
        cursor.execute('SELECT id, username FROM users')
    users = cursor.fetchall()
    conn.close()
    return render_template('borrowerprofile.html', users=users, search=search)

@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if not session.get('logged_in') or session.get('user_type') != 'admin':
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT username FROM users WHERE id = %s', (user_id,))
    result = cursor.fetchone()
    if result:
        username = result['username']
        # Find all books currently borrowed by this user
        cursor.execute('''
            SELECT b.id FROM books b
            JOIN (
                SELECT book_id, MAX(borrower_date) as max_date
                FROM booklog
                GROUP BY book_id
            ) bl ON b.id = bl.book_id
            JOIN booklog l ON l.book_id = bl.book_id AND l.borrower_date = bl.max_date
            WHERE l.borrower_name = %s AND l.status != 'Returned'
        ''', (username,))
        book_ids = [row['id'] for row in cursor.fetchall()]
        # Set those books to available
        for book_id in book_ids:
            cursor.execute('UPDATE books SET status = \"Available\" WHERE id = %s', (book_id,))
    # Remove collections made by this user (if you have a collections table with user_id)
    cursor.execute('DELETE FROM collections WHERE user_id = %s', (user_id,))
    # Delete the user
    cursor.execute('DELETE FROM users WHERE id = %s', (user_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('borrowerprofile'))

@app.route('/bookcatalog')
def bookcatalog():
    if not session.get('logged_in') or session.get('user_type') != 'admin':
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM books ORDER BY title')
    books = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('bookcatalog.html', books=books)

@app.route('/edit_book/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    if not session.get('logged_in') or session.get('user_type') != 'admin':
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        isbn = request.form['isbn']
        year_published = request.form.get('year_published')
        genre = request.form.get('genre')
        status = request.form.get('status', 'available')
        cursor.execute('''
            UPDATE books SET title=%s, author=%s, isbn=%s, year_published=%s, genre=%s, status=%s WHERE id=%s
        ''', (title, author, isbn, year_published, genre, status, book_id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('bookcatalog'))
    else:
        cursor.execute('SELECT * FROM books WHERE id = %s', (book_id,))
        book = cursor.fetchone()
        cursor.close()
        conn.close()
        if not book:
            return redirect(url_for('bookcatalog'))
        return render_template('edit_book.html', book=book)

@app.route('/delete_book/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    if not session.get('logged_in') or session.get('user_type') != 'admin':
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM books WHERE id = %s', (book_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('bookcatalog'))

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if not session.get('logged_in') or session.get('user_type') != 'admin':
        return redirect(url_for('login'))
    message = None
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        isbn = request.form['isbn']
        year_published = request.form.get('year_published')
        genre = request.form.get('genre')
        status = request.form.get('status', 'available')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO books (title, author, isbn, year_published, genre, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (title, author, isbn, year_published, genre, status))
        conn.commit()
        cursor.close()
        conn.close()
        message = 'Book added successfully!'
    return render_template('add_book.html', message=message)

if __name__ == '__main__':
    app.run(debug=True)
