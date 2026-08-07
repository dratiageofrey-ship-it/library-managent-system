from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>Library Management System - WORKING!</h1><a href="/login"><button>Go to Login</button></a>'

@app.route('/login')
def login():
    return '''<html><body><h1>Login</h1><form method="POST">
        <input type="text" name="username" placeholder="Username"><br>
        <input type="password" name="password" placeholder="Password"><br>
        <button>Login</button></form>
        <p>Demo: admin1 / admin123</p></body></html>'''

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
