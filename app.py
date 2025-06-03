from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'secret'
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

users = {}  # In-memory "DB"

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if 'login' in request.form:
            username = request.form['username']
            password = request.form['password']
            user = users.get(username)
            if user and user['password'] == password:
                session['username'] = username
                return redirect(url_for('profile'))
            else:
                error = "Invalid username or password."
        elif 'register' in request.form:
            return redirect(url_for('register'))
    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        if username in users:
            return render_template('register.html', message="Username already taken!")

        password = request.form['password']
        name = request.form['name']
        age = request.form['age']
        address = request.form['address']

        file = request.files['image']
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        users[username] = {
            'password': password,
            'name': name,
            'age': age,
            'address': address,
            'image': filename
        }
        # Redirect to login after successful registration
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/profile')
def profile():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
    user = users.get(username)
    return render_template('profile.html', user=user)

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)
