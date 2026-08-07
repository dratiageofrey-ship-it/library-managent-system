from flask import Flask, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = 'library_secret_key_2026'

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin1' and password == 'admin123':
            session['username'] = username
            session['user_id'] = 1
            return redirect(url_for('dashboard'))
        return '<html><body><h1>Invalid credentials</h1><a href="/login">Try again</a></body></html>'
    
    return '''<html><body style="text-align:center; padding:50px;">
    <h1>Library Management System - Login</h1>
    <form method="POST">
        <input type="text" name="username" placeholder="Username" required><br><br>
        <input type="password" name="password" placeholder="Password" required><br><br>
        <button type="submit">Login</button>
    </form>
    <p>Demo: username=<b>admin1</b>, password=<b>admin123</b></p>
    </body></html>'''

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return '<html><body><h1>Welcome to Dashboard!</h1><p>You are logged in as: ' + session.get('username') + '</p><a href="/logout">Logout</a></body></html>'

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
