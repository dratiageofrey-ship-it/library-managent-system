from flask import Flask, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = 'library'

HTML_LOGIN = '''<!DOCTYPE html><html><head><title>Login</title><style>
body{font-family:Arial;text-align:center;padding:50px;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%)}
.box{background:white;padding:30px;border-radius:8px;max-width:400px;margin:auto;box-shadow:0 10px 25px rgba(0,0,0,0.2)}
h1{color:#2c3e50;margin-bottom:20px}
input{width:100%;padding:10px;margin:10px 0;border:1px solid #ddd;border-radius:4px;font-size:16px}
button{width:100%;padding:10px;background:#667eea;color:white;border:none;border-radius:4px;cursor:pointer;font-weight:bold}
button:hover{background:#764ba2}
</style></head><body><div class="box">
<h1>📚 Library Management System</h1>
<form method="POST">
<input type="text" name="username" placeholder="Username" required>
<input type="password" name="password" placeholder="Password" required>
<button type="submit">Login</button>
</form>
<p style="margin-top:20px;color:#666">Demo: admin1 / admin123</p>
</div></body></html>'''

HTML_DASHBOARD = '''<!DOCTYPE html><html><head><title>Dashboard</title><style>
body{font-family:Arial;margin:0;background:#f5f5f5}
.nav{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;padding:15px 20px;display:flex;justify-content:space-between;align-items:center}
.nav a{color:white;margin-left:20px;text-decoration:none}
.nav a:hover{opacity:0.8}
.content{padding:20px;max-width:1200px;margin:auto}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:20px}
.card{background:white;padding:20px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.1);border-left:4px solid #667eea}
.card h3{color:#666;font-size:12px;text-transform:uppercase;margin-bottom:10px}
.card .number{font-size:32px;font-weight:bold;color:#2c3e50}
</style></head><body>
<div class="nav">
<h1>📚 Library Management System</h1>
<div>Welcome, admin1 | <a href="/logout">Logout</a></div>
</div>
<div class="content">
<h2>Dashboard</h2>
<div class="grid">
<div class="card"><h3>Total Books</h3><div class="number">5</div></div>
<div class="card"><h3>Total Members</h3><div class="number">5</div></div>
<div class="card"><h3>Active Loans</h3><div class="number">3</div></div>
<div class="card"><h3>Pending Fines</h3><div class="number">0</div></div>
</div>
<h3 style="margin-top:30px">Navigation</h3>
<p><a href="/books" style="margin-right:20px">📖 Books</a>
<a href="/members" style="margin-right:20px">👥 Members</a>
<a href="/loans" style="margin-right:20px">📋 Loans</a>
<a href="/fines" style="margin-right:20px">💰 Fines</a>
<a href="/reports">📈 Reports</a></p>
</div></body></html>'''

HTML_LIST = '''<!DOCTYPE html><html><head><title>{title}</title><style>
body{font-family:Arial;margin:0;background:#f5f5f5}
.nav{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;padding:15px 20px;display:flex;justify-content:space-between}
.nav a{color:white;text-decoration:none;margin-right:20px}
.content{padding:20px;max-width:1000px;margin:auto}
table{width:100%;background:white;border-collapse:collapse;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.1)}
th{background:#34495e;color:white;padding:10px;text-align:left}
td{padding:10px;border-bottom:1px solid #ecf0f1}
tr:hover{background:#f9f9f9}
</style></head><body>
<div class="nav">
<h1>📚 Library Management</h1>
<a href="/dashboard">Dashboard</a>
<a href="/logout">Logout</a>
</div>
<div class="content">
<h2>{title}</h2>
{content}
</div></body></html>'''

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('username') == 'admin1' and request.form.get('password') == 'admin123':
            session['username'] = 'admin1'
            return redirect(url_for('dashboard'))
    return HTML_LOGIN

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return HTML_DASHBOARD

@app.route('/books')
def books():
    if 'username' not in session:
        return redirect(url_for('login'))
    content = '<table><tr><th>ID</th><th>Title</th><th>Author</th><th>Category</th></tr><tr><td colspan="4">No books yet</td></tr></table>'
    return HTML_LIST.format(title='Books', content=content)

@app.route('/members')
def members():
    if 'username' not in session:
        return redirect(url_for('login'))
    content = '<table><tr><th>ID</th><th>Name</th><th>Email</th><th>Phone</th></tr><tr><td colspan="4">No members yet</td></tr></table>'
    return HTML_LIST.format(title='Members', content=content)

@app.route('/loans')
def loans():
    if 'username' not in session:
        return redirect(url_for('login'))
    content = '<table><tr><th>ID</th><th>Book</th><th>Member</th><th>Due Date</th></tr><tr><td colspan="4">No loans yet</td></tr></table>'
    return HTML_LIST.format(title='Loans', content=content)

@app.route('/fines')
def fines():
    if 'username' not in session:
        return redirect(url_for('login'))
    content = '<table><tr><th>ID</th><th>Member</th><th>Amount</th><th>Status</th></tr><tr><td colspan="4">No fines yet</td></tr></table>'
    return HTML_LIST.format(title='Fines', content=content)

@app.route('/reports')
def reports():
    if 'username' not in session:
        return redirect(url_for('login'))
    content = '<p>Reports coming soon</p>'
    return HTML_LIST.format(title='Reports', content=content)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
