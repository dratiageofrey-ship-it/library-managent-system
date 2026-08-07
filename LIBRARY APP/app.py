from flask import Flask, render_template, request, redirect, url_for, session
import os

# Create Flask app with explicit template folder
app = Flask(__name__, template_folder='templates')
app.secret_key = 'library_secret_key_2026'

def get_db_connection():
    import psycopg2
    DB_URL = os.environ.get('DATABASE_PUBLIC_URL', 'postgresql://postgres:Library123@crossover.proxy.rlwy.net:59153/railway')
    return psycopg2.connect(DB_URL)

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Demo login
        if username == 'admin1' and password == 'admin123':
            session['username'] = username
            session['user_id'] = 1
            return redirect(url_for('dashboard'))
        
        return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute('SELECT COUNT(*) as total FROM books')
        total_books = cur.fetchone()['total'] if cur.fetchone() else 0
        
        cur.execute('SELECT COUNT(*) as total FROM members')
        total_members = cur.fetchone()['total'] if cur.fetchone() else 0
        
        cur.execute('SELECT COUNT(*) as total FROM loans WHERE status = %s', ('ACTIVE',))
        active_loans = cur.fetchone()['total'] if cur.fetchone() else 0
        
        cur.close()
        conn.close()
        
        return render_template('dashboard.html',
                             total_books=total_books,
                             total_members=total_members,
                             active_loans=active_loans,
                             pending_fines=0,
                             recent_loans=[])
    except Exception as e:
        return render_template('dashboard.html',
                             total_books=0,
                             total_members=0,
                             active_loans=0,
                             pending_fines=0,
                             recent_loans=[],
                             error=str(e))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/books')
def books():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('SELECT * FROM books ORDER BY book_id DESC')
        books_list = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('books.html', books=books_list)
    except Exception as e:
        return render_template('books.html', books=[], error=str(e))

@app.route('/members')
def members():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('SELECT * FROM members ORDER BY member_id DESC')
        members_list = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('members.html', members=members_list)
    except Exception as e:
        return render_template('members.html', members=[], error=str(e))

@app.route('/loans')
def loans():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('''
            SELECT l.loan_id, b.title, m.first_name, m.last_name, l.loan_date, l.due_date, l.return_date, l.status
            FROM loans l
            JOIN books b ON l.book_id = b.book_id
            JOIN members m ON l.member_id = m.member_id
            ORDER BY l.loan_id DESC
        ''')
        loans_list = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('loans.html', loans=loans_list)
    except Exception as e:
        return render_template('loans.html', loans=[], error=str(e))

@app.route('/fines')
def fines():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('''
            SELECT f.fine_id, m.first_name, m.last_name, f.fine_amount, f.reason, f.status
            FROM fines f
            JOIN members m ON f.member_id = m.member_id
            ORDER BY f.fine_id DESC
        ''')
        fines_list = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('fines.html', fines=fines_list)
    except Exception as e:
        return render_template('fines.html', fines=[], error=str(e))

@app.route('/reports')
def reports():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    return render_template('reports.html', most_borrowed=[], overdue=[])

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
