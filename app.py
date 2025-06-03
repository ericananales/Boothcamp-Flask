from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import os
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
DB_NAME = 'users.db'

# Initialize DB
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                address TEXT NOT NULL,
                image TEXT NOT NULL
            )
        ''')
init_db()

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if 'login' in request.form:
            username = request.form['username']
            password = request.form['password']
            with sqlite3.connect(DB_NAME) as conn:
                cur = conn.cursor()
                cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
                user = cur.fetchone()
            if user:
                session['username'] = username
                return redirect(url_for('home'))
            else:
                error = "Invalid username or password."
        elif 'register' in request.form:
            return redirect(url_for('register'))
    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    message = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        age = request.form['age']
        address = request.form['address']
        file = request.files['image']

        if not file:
            message = "Please upload an image."
            return render_template('register.html', message=message)

        filename = secure_filename(file.filename)
        if not filename:
            message = "Invalid file name."
            return render_template('register.html', message=message)

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            with sqlite3.connect(DB_NAME) as conn:
                cur = conn.cursor()
                cur.execute("INSERT INTO users (username, password, name, age, address, image) VALUES (?, ?, ?, ?, ?, ?)",
                            (username, password, name, int(age), address, filename))
                conn.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            message = "Username already taken!"
    return render_template('register.html', message=message)

@app.route('/home')
def home():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))

    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("SELECT name, age, address, image FROM users WHERE username=?", (username,))
        user_data = cur.fetchone()

    if user_data:
        user = {
            'name': user_data[0],
            'age': user_data[1],
            'address': user_data[2],
            'image': user_data[3]
        }
        return render_template('home.html', user=user)

    return redirect(url_for('login'))


@app.route('/profile')
def profile():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("SELECT name, age, address, image FROM users WHERE username=?", (username,))
        user_data = cur.fetchone()

    if user_data:
        user = {
            'name': user_data[0],
            'age': user_data[1],
            'address': user_data[2],
            'image': user_data[3]
        }
        return render_template('profile.html', user=user)
    return "User not found", 404

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)
