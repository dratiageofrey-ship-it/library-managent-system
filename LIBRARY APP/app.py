from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_cors import CORS
import os
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
app.secret_key = 'library_secret_key_2026'
CORS(app)

# Lazy import psycopg2 only when needed
def get_db_connection():
    import psycopg2
    from psycopg2.extras import RealDictCursor
    DB_URL = os.environ.get('DATABASE_PUBLIC_URL', 'postgresql://postgres:Library123@crossover.proxy.rlwy.net:59153/railway')
    conn = psycopg2.connect(DB_URL)
    return conn

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== AUTHENTICATION ====================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            
            conn = get_db_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
            user = cur.fetchone()
            cur.close()
            conn.close()
            
            if user:
                session['user_id'] = user['user_id']
                session['username'] = user['username']
                session['role'] = user['role']
                return redirect(url_for('dashboard'))
            else:
                return render_template('login.html', error='Invalid credentials')
        except Exception as e:
            return render_template('login.html', error=f'Database error: {str(e)}')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ==================== DASHBOARD ====================

@app.route('/')
@login_required
def dashboard():
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get statistics
        cur.execute('SELECT COUNT(*) as total FROM books')
        total_books = cur.fetchone()['total']
        
        cur.execute('SELECT COUNT(*) as total FROM members')
        total_members = cur.fetchone()['total']
        
        cur.execute('SELECT COUNT(*) as total FROM loans WHERE status = %s', ('ACTIVE',))
        active_loans = cur.fetchone()['total']
        
        cur.execute('SELECT SUM(fine_amount) as total FROM fines WHERE status = %s', ('PENDING',))
        result = cur.fetchone()
        pending_fines = result['total'] if result['total'] else 0
        
        # Recent loans
        cur.execute('''
            SELECT l.loan_id, b.title, m.first_name, m.last_name, l.loan_date, l.due_date
            FROM loans l
            JOIN books b ON l.book_id = b.book_id
            JOIN members m ON l.member_id = m.member_id
            ORDER BY l.loan_date DESC LIMIT 5
        ''')
        recent_loans = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return render_template('dashboard.html', 
                             total_books=total_books,
                             total_members=total_members,
                             active_loans=active_loans,
                             pending_fines=pending_fines,
                             recent_loans=recent_loans)
    except Exception as e:
        return render_template('dashboard.html', error=f'Error: {str(e)}',
                             total_books=0, total_members=0, active_loans=0, 
                             pending_fines=0, recent_loans=[])

# ==================== BOOKS ====================

@app.route('/books')
@login_required
def books():
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('SELECT * FROM books ORDER BY book_id DESC')
        books = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('books.html', books=books)
    except Exception as e:
        return render_template('books.html', books=[], error=str(e))

@app.route('/books/add', methods=['GET', 'POST'])
@login_required
def add_book():
    if request.method == 'POST':
        try:
            import psycopg2
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO books (isbn, title, author, publisher, publication_year, category, total_copies, available_copies, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                request.form['isbn'],
                request.form['title'],
                request.form['author'],
                request.form['publisher'],
                request.form['publication_year'],
                request.form['category'],
                request.form['total_copies'],
                request.form['total_copies'],
                'AVAILABLE'
            ))
            conn.commit()
            cur.close()
            conn.close()
            return redirect(url_for('books'))
        except Exception as e:
            return render_template('add_book.html', error=str(e))
    
    return render_template('add_book.html')

# ==================== MEMBERS ====================

@app.route('/members')
@login_required
def members():
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

@app.route('/members/add', methods=['GET', 'POST'])
@login_required
def add_member():
    if request.method == 'POST':
        try:
            import psycopg2
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO members (first_name, last_name, email, phone, address, membership_date, membership_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (
                request.form['first_name'],
                request.form['last_name'],
                request.form['email'],
                request.form['phone'],
                request.form['address'],
                datetime.now().date(),
                'ACTIVE'
            ))
            conn.commit()
            cur.close()
            conn.close()
            return redirect(url_for('members'))
        except Exception as e:
            return render_template('add_member.html', error=str(e))
    
    return render_template('add_member.html')

# ==================== LOANS ====================

@app.route('/loans')
@login_required
def loans():
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('''
            SELECT l.loan_id, b.title, m.first_name, m.last_name, l.loan_date, l.due_date, l.return_date, l.status, l.fine_amount
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

@app.route('/loans/borrow', methods=['GET', 'POST'])
@login_required
def borrow_book():
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        if request.method == 'POST':
            try:
                member_id = request.form['member_id']
                book_id = request.form['book_id']
                loan_days = int(request.form.get('loan_days', 14))
                
                # Check if book is available
                cur.execute('SELECT available_copies FROM books WHERE book_id = %s', (book_id,))
                book = cur.fetchone()
                
                if not book or book['available_copies'] <= 0:
                    cur.close()
                    conn.close()
                    return render_template('borrow_book.html', error='Book not available', books=[], members=[])
                
                # Create loan
                due_date = datetime.now().date() + timedelta(days=loan_days)
                cur.execute('''
                    INSERT INTO loans (book_id, member_id, loan_date, due_date, status, fine_amount)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (book_id, member_id, datetime.now().date(), due_date, 'ACTIVE', 0))
                
                # Update available copies
                cur.execute('UPDATE books SET available_copies = available_copies - 1 WHERE book_id = %s', (book_id,))
                
                conn.commit()
                cur.close()
                conn.close()
                return redirect(url_for('loans'))
            except Exception as e:
                cur.close()
                conn.close()
                return render_template('borrow_book.html', error=str(e), books=[], members=[])
        
        # Get books and members for dropdown
        cur.execute('SELECT book_id, title FROM books WHERE available_copies > 0')
        books = cur.fetchall()
        cur.execute('SELECT member_id, first_name, last_name FROM members WHERE membership_status = %s', ('ACTIVE',))
        members_list = cur.fetchall()
        
        cur.close()
        conn.close()
        return render_template('borrow_book.html', books=books, members=members_list)
    except Exception as e:
        return render_template('borrow_book.html', error=str(e), books=[], members=[])

@app.route('/loans/<int:loan_id>/return', methods=['POST'])
@login_required
def return_book(loan_id):
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get loan details
        cur.execute('SELECT book_id FROM loans WHERE loan_id = %s', (loan_id,))
        loan = cur.fetchone()
        
        # Update loan
        cur.execute('''
            UPDATE loans
            SET return_date = %s, status = %s
            WHERE loan_id = %s
        ''', (datetime.now().date(), 'RETURNED', loan_id))
        
        # Update book copies
        cur.execute('UPDATE books SET available_copies = available_copies + 1 WHERE book_id = %s', (loan['book_id'],))
        
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('loans'))
    except Exception as e:
        return redirect(url_for('loans'))

# ==================== FINES ====================

@app.route('/fines')
@login_required
def fines():
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('''
            SELECT f.fine_id, m.first_name, m.last_name, f.fine_amount, f.reason, f.status, f.created_date
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

# ==================== REPORTS ====================

@app.route('/reports')
@login_required
def reports():
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Most borrowed books
        cur.execute('''
            SELECT b.title, COUNT(l.loan_id) as borrow_count
            FROM books b
            LEFT JOIN loans l ON b.book_id = l.book_id
            GROUP BY b.book_id, b.title
            ORDER BY borrow_count DESC LIMIT 10
        ''')
        most_borrowed = cur.fetchall()
        
        # Overdue loans
        cur.execute('''
            SELECT l.loan_id, b.title, m.first_name, m.last_name, l.due_date
            FROM loans l
            JOIN books b ON l.book_id = b.book_id
            JOIN members m ON l.member_id = m.member_id
            WHERE l.status = %s AND l.due_date < %s
            ORDER BY l.due_date ASC
        ''', ('ACTIVE', datetime.now().date()))
        overdue = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return render_template('reports.html', most_borrowed=most_borrowed, overdue=overdue)
    except Exception as e:
        return render_template('reports.html', most_borrowed=[], overdue=[], error=str(e))

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
