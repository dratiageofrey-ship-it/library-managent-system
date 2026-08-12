from flask import Flask, request, redirect, url_for, session
import os
import sys

app = Flask(__name__)
app.secret_key = 'library'

def get_db_connection():
    import psycopg2
    DB_URL = os.environ.get('DATABASE_PUBLIC_URL', 'postgresql://postgres:Library123@crossover.proxy.rlwy.net:59153/railway')
    try:
        conn = psycopg2.connect(DB_URL)
        return conn
    except Exception as e:
        print(f"DB ERROR: {e}", file=sys.stderr)
        return None

# TEST CONNECTION ON STARTUP
print("Testing database connection...", file=sys.stderr)
test_conn = get_db_connection()
if test_conn:
    print("✅ Database connected!", file=sys.stderr)
    test_conn.close()
else:
    print("❌ Database connection FAILED!", file=sys.stderr)

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
    return '''<!DOCTYPE html><html><head><title>Login</title><style>
body{font-family:Arial;text-align:center;padding:50px;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%)}
.box{background:white;padding:30px;border-radius:8px;max-width:400px;margin:auto;box-shadow:0 10px 25px rgba(0,0,0,0.2)}
h1{color:#2c3e50;margin-bottom:20px}
input{width:100%;padding:10px;margin:10px 0;border:1px solid #ddd;border-radius:4px;font-size:16px;box-sizing:border-box}
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

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    total_books = 0
    total_members = 0
    active_loans = 0
    pending_fines = 0
    recent_loans_html = '<tr><td colspan="3">No loans yet</td></tr>'
    error_msg = ''
    
    try:
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            
            try:
                cur.execute('SELECT COUNT(*) FROM books')
                result = cur.fetchone()
                total_books = result[0] if result else 0
            except Exception as e:
                error_msg += f'Books error: {str(e)}<br>'
            
            try:
                cur.execute('SELECT COUNT(*) FROM members')
                result = cur.fetchone()
                total_members = result[0] if result else 0
            except Exception as e:
                error_msg += f'Members error: {str(e)}<br>'
            
            try:
                cur.execute('SELECT COUNT(*) FROM loans WHERE status = %s', ('ACTIVE',))
                result = cur.fetchone()
                active_loans = result[0] if result else 0
            except Exception as e:
                error_msg += f'Loans error: {str(e)}<br>'
            
            try:
                cur.execute('SELECT COUNT(*) FROM fines WHERE status = %s', ('PENDING',))
                result = cur.fetchone()
                pending_fines = result[0] if result else 0
            except Exception as e:
                error_msg += f'Fines error: {str(e)}<br>'
            
            cur.close()
            conn.close()
        else:
            error_msg = 'Cannot connect to database!'
    except Exception as e:
        error_msg += f'General error: {str(e)}<br>'
    
    error_display = f'<div style="background:#ffdddd;padding:10px;margin:10px 0;border-radius:4px"><strong>⚠️ DEBUG:</strong><br>{error_msg}</div>' if error_msg else ''
    
    return f'''<!DOCTYPE html><html><head><title>Dashboard</title><style>
body{{font-family:Arial;margin:0;background:#f5f5f5}}
.nav{{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;padding:15px 20px;display:flex;justify-content:space-between;align-items:center}}
.nav a{{color:white;margin-left:20px;text-decoration:none;cursor:pointer}}
.nav a:hover{{opacity:0.8}}
.content{{padding:20px;max-width:1200px;margin:auto}}
.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:20px}}
.card{{background:white;padding:20px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.1);border-left:4px solid #667eea}}
.card h3{{color:#666;font-size:12px;text-transform:uppercase;margin-bottom:10px}}
.card .number{{font-size:32px;font-weight:bold;color:#2c3e50}}
.menu{{margin:20px 0}}
.menu a{{display:inline-block;margin-right:15px;padding:10px 15px;background:#667eea;color:white;text-decoration:none;border-radius:4px;cursor:pointer}}
.menu a:hover{{background:#764ba2}}
table{{width:100%;background:white;border-collapse:collapse;border-radius:8px;margin-top:20px;box-shadow:0 2px 8px rgba(0,0,0,0.1)}}
th{{background:#34495e;color:white;padding:10px;text-align:left}}
td{{padding:10px;border-bottom:1px solid #ecf0f1;font-size:14px}}
</style></head><body>
<div class="nav"><h1>📚 Library Management System</h1><div>Welcome, admin1 | <a href="/logout">Logout</a></div></div>
<div class="content">
{error_display}
<h2>Dashboard</h2>
<div class="grid">
<div class="card"><h3>Total Books</h3><div class="number">{total_books}</div></div>
<div class="card"><h3>Total Members</h3><div class="number">{total_members}</div></div>
<div class="card"><h3>Active Loans</h3><div class="number">{active_loans}</div></div>
<div class="card"><h3>Pending Fines</h3><div class="number">{pending_fines}</div></div>
</div>
<div class="menu">
<a href="/books">📖 Books</a>
<a href="/members">👥 Members</a>
<a href="/loans">📋 Loans</a>
<a href="/fines">💰 Fines</a>
<a href="/reports">📈 Reports</a>
</div>
</div></body></html>'''

@app.route('/books', methods=['GET', 'POST'])
def books():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    error = ''
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            if conn:
                cur = conn.cursor()
                print(f"Inserting book: {request.form}", file=sys.stderr)
                cur.execute('''INSERT INTO books (isbn, title, author, publisher, publication_year, category, total_copies, available_copies, status) 
                              VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'AVAILABLE')''',
                           (request.form['isbn'], request.form['title'], request.form['author'], request.form['publisher'],
                            int(request.form['publication_year']), request.form['category'], int(request.form['total_copies']), int(request.form['total_copies'])))
                conn.commit()
                print("✅ Book inserted successfully", file=sys.stderr)
                cur.close()
                conn.close()
            else:
                error = "Database connection failed!"
        except Exception as e:
            error = f"Insert error: {str(e)}"
            print(f"❌ Book insert error: {e}", file=sys.stderr)
        return redirect(url_for('books'))
    
    rows = '<table><tr><th>ID</th><th>Title</th><th>Author</th><th>Category</th><th>Available</th><th>Action</th></tr>'
    try:
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            cur.execute('SELECT book_id, title, author, category, available_copies FROM books ORDER BY book_id DESC')
            books_data = cur.fetchall()
            print(f"Books query returned: {len(books_data) if books_data else 0} rows", file=sys.stderr)
            if books_data:
                for bid, title, author, cat, avail in books_data:
                    rows += f'<tr><td>{bid}</td><td>{title}</td><td>{author}</td><td>{cat}</td><td>{avail}</td><td><a href="/delete_book/{bid}" onclick="return confirm(\'Delete?\')" style="color:red">Delete</a></td></tr>'
            else:
                rows += '<tr><td colspan="6">No books in database</td></tr>'
            cur.close()
            conn.close()
        else:
            rows += '<tr><td colspan="6">Database connection failed</td></tr>'
    except Exception as e:
        rows += f'<tr><td colspan="6">Error: {str(e)}</td></tr>'
        print(f"❌ Books query error: {e}", file=sys.stderr)
    rows += '</table>'
    
    error_html = f'<div style="background:#ffdddd;padding:10px;margin:10px 0;border-radius:4px">{error}</div>' if error else ''
    
    return f'''<!DOCTYPE html><html><head><title>Books</title><style>
body{{font-family:Arial;margin:0;background:#f5f5f5}}
.nav{{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;padding:15px 20px;display:flex;justify-content:space-between}}
.nav a{{color:white;text-decoration:none;margin-right:20px;cursor:pointer}}
.content{{padding:20px;max-width:1200px;margin:auto}}
.btn{{padding:10px 15px;background:#667eea;color:white;border:none;border-radius:4px;cursor:pointer;font-weight:bold;margin-bottom:20px}}
.form-box{{background:white;padding:20px;border-radius:8px;max-width:400px;margin:20px 0;display:none}}
.form-box.show{{display:block}}
.form-box input{{width:100%;padding:8px;margin:8px 0;border:1px solid #ddd;border-radius:4px;box-sizing:border-box}}
.form-box button{{width:100%;padding:10px;background:#667eea;color:white;border:none;border-radius:4px;cursor:pointer}}
table{{width:100%;background:white;border-collapse:collapse;border-radius:8px}}
th{{background:#34495e;color:white;padding:12px;text-align:left}}
td{{padding:10px;border-bottom:1px solid #ecf0f1}}
</style></head><body>
<div class="nav"><h1>📚 Books</h1><div><a href="/dashboard">Dashboard</a><a href="/logout">Logout</a></div></div>
<div class="content">
{error_html}
<button class="btn" id="toggleBtn" onclick="toggleForm()">+ Add Book</button>
<div id="form" class="form-box">
<h3>Add New Book</h3>
<form method="POST">
<input type="text" name="isbn" placeholder="ISBN" required>
<input type="text" name="title" placeholder="Title" required>
<input type="text" name="author" placeholder="Author" required>
<input type="text" name="publisher" placeholder="Publisher" required>
<input type="number" name="publication_year" placeholder="Year" required>
<input type="text" name="category" placeholder="Category" required>
<input type="number" name="total_copies" placeholder="Copies" value="1" required>
<button type="submit">Add</button>
</form>
</div>
{rows}
</div>
<script>function toggleForm(){{document.getElementById('form').classList.toggle('show')}}</script>
</body></html>'''

@app.route('/delete_book/<int:book_id>')
def delete_book(book_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    try:
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            cur.execute('DELETE FROM books WHERE book_id=%s', (book_id,))
            conn.commit()
            cur.close()
            conn.close()
    except:
        pass
    return redirect(url_for('books'))

@app.route('/members', methods=['GET', 'POST'])
def members():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    error = ''
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            if conn:
                cur = conn.cursor()
                print(f"Inserting member: {request.form}", file=sys.stderr)
                cur.execute('''INSERT INTO members (first_name, last_name, email, phone, address, membership_date, membership_status) 
                              VALUES (%s, %s, %s, %s, %s, CURRENT_DATE, 'ACTIVE')''',
                           (request.form['first_name'], request.form['last_name'], request.form['email'], request.form['phone'], request.form['address']))
                conn.commit()
                print("✅ Member inserted successfully", file=sys.stderr)
                cur.close()
                conn.close()
            else:
                error = "Database connection failed!"
        except Exception as e:
            error = f"Insert error: {str(e)}"
            print(f"❌ Member insert error: {e}", file=sys.stderr)
        return redirect(url_for('members'))
    
    rows = '<table><tr><th>ID</th><th>Name</th><th>Email</th><th>Phone</th><th>Status</th><th>Action</th></tr>'
    try:
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            cur.execute('SELECT member_id, first_name, last_name, email, phone, membership_status FROM members ORDER BY member_id DESC')
            members_data = cur.fetchall()
            print(f"Members query returned: {len(members_data) if members_data else 0} rows", file=sys.stderr)
            if members_data:
                for mid, fname, lname, email, phone, status in members_data:
                    rows += f'<tr><td>{mid}</td><td>{fname} {lname}</td><td>{email}</td><td>{phone}</td><td>{status}</td><td><a href="/delete_member/{mid}" onclick="return confirm(\'Delete?\')" style="color:red">Delete</a></td></tr>'
            else:
                rows += '<tr><td colspan="6">No members in database</td></tr>'
            cur.close()
            conn.close()
        else:
            rows += '<tr><td colspan="6">Database connection failed</td></tr>'
    except Exception as e:
        rows += f'<tr><td colspan="6">Error: {str(e)}</td></tr>'
        print(f"❌ Members query error: {e}", file=sys.stderr)
    rows += '</table>'
    
    error_html = f'<div style="background:#ffdddd;padding:10px;margin:10px 0;border-radius:4px">{error}</div>' if error else ''
    
    return f'''<!DOCTYPE html><html><head><title>Members</title><style>
body{{font-family:Arial;margin:0;background:#f5f5f5}}
.nav{{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;padding:15px 20px;display:flex;justify-content:space-between}}
.nav a{{color:white;text-decoration:none;margin-right:20px;cursor:pointer}}
.content{{padding:20px;max-width:1200px;margin:auto}}
.btn{{padding:10px 15px;background:#667eea;color:white;border:none;border-radius:4px;cursor:pointer;font-weight:bold;margin-bottom:20px}}
.form-box{{background:white;padding:20px;border-radius:8px;max-width:400px;margin:20px 0;display:none}}
.form-box.show{{display:block}}
.form-box input{{width:100%;padding:8px;margin:8px 0;border:1px solid #ddd;border-radius:4px;box-sizing:border-box}}
.form-box button{{width:100%;padding:10px;background:#667eea;color:white;border:none;border-radius:4px;cursor:pointer}}
table{{width:100%;background:white;border-collapse:collapse;border-radius:8px}}
th{{background:#34495e;color:white;padding:12px;text-align:left}}
td{{padding:10px;border-bottom:1px solid #ecf0f1}}
</style></head><body>
<div class="nav"><h1>📚 Members</h1><div><a href="/dashboard">Dashboard</a><a href="/logout">Logout</a></div></div>
<div class="content">
{error_html}
<button class="btn" id="toggleBtn" onclick="toggleForm()">+ Add Member</button>
<div id="form" class="form-box">
<h3>Add New Member</h3>
<form method="POST">
<input type="text" name="first_name" placeholder="First Name" required>
<input type="text" name="last_name" placeholder="Last Name" required>
<input type="email" name="email" placeholder="Email" required>
<input type="text" name="phone" placeholder="Phone" required>
<input type="text" name="address" placeholder="Address" required>
<button type="submit">Add</button>
</form>
</div>
{rows}
</div>
<script>function toggleForm(){{document.getElementById('form').classList.toggle('show')}}</script>
</body></html>'''

@app.route('/delete_member/<int:member_id>')
def delete_member(member_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    try:
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            cur.execute('DELETE FROM members WHERE member_id=%s', (member_id,))
            conn.commit()
            cur.close()
            conn.close()
    except:
        pass
    return redirect(url_for('members'))

@app.route('/loans')
def loans():
    if 'username' not in session:
        return redirect(url_for('login'))
    rows = '<table><tr><th>ID</th><th>Book</th><th>Member</th><th>Due Date</th></tr>'
    try:
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            cur.execute('SELECT l.loan_id, b.title, m.first_name, m.last_name, l.due_date FROM loans l LEFT JOIN books b ON l.book_id = b.book_id LEFT JOIN members m ON l.member_id = m.member_id LIMIT 10')
            for lid, title, fname, lname, due in cur.fetchall():
                rows += f'<tr><td>{lid}</td><td>{title}</td><td>{fname} {lname}</td><td>{due}</td></tr>'
            cur.close()
            conn.close()
    except:
        pass
    rows += '</table>'
    return f'''<!DOCTYPE html><html><head><title>Loans</title><style>body{{font-family:Arial;margin:0;background:#f5f5f5}}.nav{{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;padding:15px 20px}}.content{{padding:20px;max-width:1200px;margin:auto}}table{{width:100%;background:white;border-collapse:collapse}}th{{background:#34495e;color:white;padding:12px}}td{{padding:10px;border-bottom:1px solid #ecf0f1}}</style></head><body><div class="nav"><h1>📚 Loans</h1><a href="/dashboard" style="color:white;text-decoration:none">Dashboard</a></div><div class="content">{rows}</div></body></html>'''

@app.route('/fines')
def fines():
    if 'username' not in session:
        return redirect(url_for('login'))
    return f'''<!DOCTYPE html><html><head><title>Fines</title><style>body{{font-family:Arial;margin:0;background:#f5f5f5}}</style></head><body><div style="padding:20px"><h1>Fines</h1><p>Fines module</p><a href="/dashboard">Back</a></div></body></html>'''

@app.route('/reports')
def reports():
    if 'username' not in session:
        return redirect(url_for('login'))
    return f'''<!DOCTYPE html><html><head><title>Reports</title><style>body{{font-family:Arial;margin:0;background:#f5f5f5}}</style></head><body><div style="padding:20px"><h1>Reports</h1><p>Reports module</p><a href="/dashboard">Back</a></div></body></html>'''

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
