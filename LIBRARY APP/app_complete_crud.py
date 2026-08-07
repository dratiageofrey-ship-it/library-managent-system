from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime, timedelta
import os

app = Flask(__name__, template_folder='templates')
app.secret_key = 'library_secret_key_2026'

def get_db_connection():
    import psycopg2
    DB_URL = os.environ.get('DATABASE_PUBLIC_URL', 'postgresql://postgres:Library123@crossover.proxy.rlwy.net:59153/railway')
    return psycopg2.connect(DB_URL)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

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
        if username == 'admin1' and password == 'admin123':
            session['username'] = username
            session['user_id'] = 1
            return redirect(url_for('dashboard'))
        flash('Invalid credentials', 'error')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute('SELECT COUNT(*) as total FROM books')
        total_books = cur.fetchone()['total']
        cur.execute('SELECT COUNT(*) as total FROM members')
        total_members = cur.fetchone()['total']
        cur.execute('SELECT COUNT(*) as total FROM loans WHERE status = %s', ('ACTIVE',))
        active_loans = cur.fetchone()['total']
        cur.execute('SELECT COALESCE(SUM(fine_amount), 0) as total FROM fines WHERE status = %s', ('PENDING',))
        pending_fines = cur.fetchone()['total']
        
        cur.execute('''SELECT l.loan_id, b.title, m.first_name, m.last_name, l.loan_date, l.due_date
                       FROM loans l JOIN books b ON l.book_id = b.book_id JOIN members m ON l.member_id = m.member_id
                       WHERE l.status = 'ACTIVE' ORDER BY l.loan_date DESC LIMIT 5''')
        recent_loans = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('dashboard.html', total_books=total_books, total_members=total_members, active_loans=active_loans, pending_fines=pending_fines, recent_loans=recent_loans)
    except Exception as e:
        return render_template('dashboard.html', total_books=0, total_members=0, active_loans=0, pending_fines=0, recent_loans=[], error=str(e))

@app.route('/books')
@login_required
def books():
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
        return render_template('books.html', books=[])

@app.route('/books/add', methods=['GET', 'POST'])
@login_required
def add_book():
    if request.method == 'POST':
        try:
            import psycopg2
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('''INSERT INTO books (isbn, title, author, publisher, publication_year, category, total_copies, available_copies, status)
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                       (request.form['isbn'], request.form['title'], request.form['author'], request.form['publisher'],
                        request.form['publication_year'], request.form['category'], request.form['total_copies'],
                        request.form['total_copies'], 'AVAILABLE'))
            conn.commit()
            cur.close()
            conn.close()
            flash('Book added successfully!', 'success')
            return redirect(url_for('books'))
        except Exception as e:
            flash(f'Error adding book: {str(e)}', 'error')
    return render_template('add_book.html')

@app.route('/books/<int:book_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        if request.method == 'POST':
            cur.execute('''UPDATE books SET title=%s, author=%s, publisher=%s, publication_year=%s, category=%s WHERE book_id=%s''',
                       (request.form['title'], request.form['author'], request.form['publisher'], request.form['publication_year'], request.form['category'], book_id))
            conn.commit()
            cur.close()
            conn.close()
            flash('Book updated successfully!', 'success')
            return redirect(url_for('books'))
        
        cur.execute('SELECT * FROM books WHERE book_id=%s', (book_id,))
        book = cur.fetchone()
        cur.close()
        conn.close()
        return render_template('edit_book.html', book=book)
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('books'))

@app.route('/books/<int:book_id>/delete', methods=['POST'])
@login_required
def delete_book(book_id):
    try:
        import psycopg2
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('DELETE FROM books WHERE book_id=%s', (book_id,))
        conn.commit()
        cur.close()
        conn.close()
        flash('Book deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    return redirect(url_for('books'))

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
        return render_template('members.html', members=[])

@app.route('/members/add', methods=['GET', 'POST'])
@login_required
def add_member():
    if request.method == 'POST':
        try:
            import psycopg2
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('''INSERT INTO members (first_name, last_name, email, phone, address, membership_date, membership_status)
                          VALUES (%s, %s, %s, %s, %s, %s, %s)''',
                       (request.form['first_name'], request.form['last_name'], request.form['email'], request.form['phone'],
                        request.form['address'], datetime.now().date(), 'ACTIVE'))
            conn.commit()
            cur.close()
            conn.close()
            flash('Member added successfully!', 'success')
            return redirect(url_for('members'))
        except Exception as e:
            flash(f'Error adding member: {str(e)}', 'error')
    return render_template('add_member.html')

@app.route('/members/<int:member_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_member(member_id):
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        if request.method == 'POST':
            cur.execute('''UPDATE members SET first_name=%s, last_name=%s, email=%s, phone=%s, address=%s, membership_status=%s WHERE member_id=%s''',
                       (request.form['first_name'], request.form['last_name'], request.form['email'], request.form['phone'],
                        request.form['address'], request.form['membership_status'], member_id))
            conn.commit()
            cur.close()
            conn.close()
            flash('Member updated successfully!', 'success')
            return redirect(url_for('members'))
        
        cur.execute('SELECT * FROM members WHERE member_id=%s', (member_id,))
        member = cur.fetchone()
        cur.close()
        conn.close()
        return render_template('edit_member.html', member=member)
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('members'))

@app.route('/loans')
@login_required
def loans():
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('''SELECT l.loan_id, b.title, m.first_name, m.last_name, l.loan_date, l.due_date, l.return_date, l.status
                       FROM loans l JOIN books b ON l.book_id = b.book_id JOIN members m ON l.member_id = m.member_id ORDER BY l.loan_id DESC''')
        loans_list = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('loans.html', loans=loans_list)
    except Exception as e:
        return render_template('loans.html', loans=[])

@app.route('/loans/borrow', methods=['GET', 'POST'])
@login_required
def borrow_book():
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        if request.method == 'POST':
            member_id = request.form['member_id']
            book_id = request.form['book_id']
            loan_days = int(request.form.get('loan_days', 14))
            
            cur.execute('SELECT available_copies FROM books WHERE book_id=%s', (book_id,))
            book = cur.fetchone()
            
            if not book or book['available_copies'] <= 0:
                flash('Book not available!', 'error')
                cur.close()
                conn.close()
                return redirect(url_for('borrow_book'))
            
            due_date = datetime.now().date() + timedelta(days=loan_days)
            cur.execute('''INSERT INTO loans (book_id, member_id, loan_date, due_date, status, fine_amount)
                          VALUES (%s, %s, %s, %s, %s, %s)''',
                       (book_id, member_id, datetime.now().date(), due_date, 'ACTIVE', 0))
            cur.execute('UPDATE books SET available_copies = available_copies - 1 WHERE book_id=%s', (book_id,))
            conn.commit()
            cur.close()
            conn.close()
            flash('Book borrowed successfully!', 'success')
            return redirect(url_for('loans'))
        
        cur.execute('SELECT book_id, title FROM books WHERE available_copies > 0 ORDER BY title')
        books = cur.fetchall()
        cur.execute('SELECT member_id, first_name, last_name FROM members WHERE membership_status=%s ORDER BY first_name', ('ACTIVE',))
        members_list = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('borrow_book.html', books=books, members=members_list)
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return render_template('borrow_book.html', books=[], members=[])

@app.route('/loans/<int:loan_id>/return', methods=['POST'])
@login_required
def return_book(loan_id):
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute('SELECT book_id FROM loans WHERE loan_id=%s', (loan_id,))
        loan = cur.fetchone()
        
        cur.execute('''UPDATE loans SET return_date=%s, status=%s WHERE loan_id=%s''',
                   (datetime.now().date(), 'RETURNED', loan_id))
        cur.execute('UPDATE books SET available_copies = available_copies + 1 WHERE book_id=%s', (loan['book_id'],))
        conn.commit()
        cur.close()
        conn.close()
        flash('Book returned successfully!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    return redirect(url_for('loans'))

@app.route('/fines')
@login_required
def fines():
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('''SELECT f.fine_id, m.first_name, m.last_name, f.fine_amount, f.reason, f.status FROM fines f
                       JOIN members m ON f.member_id = m.member_id ORDER BY f.fine_id DESC''')
        fines_list = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('fines.html', fines=fines_list)
    except Exception as e:
        return render_template('fines.html', fines=[])

@app.route('/fines/<int:fine_id>/pay', methods=['POST'])
@login_required
def pay_fine(fine_id):
    try:
        import psycopg2
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('UPDATE fines SET status=%s, paid_date=%s WHERE fine_id=%s', ('PAID', datetime.now().date(), fine_id))
        conn.commit()
        cur.close()
        conn.close()
        flash('Fine paid successfully!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    return redirect(url_for('fines'))

@app.route('/reports')
@login_required
def reports():
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute('''SELECT b.title, COUNT(l.loan_id) as borrow_count FROM books b
                       LEFT JOIN loans l ON b.book_id = l.book_id GROUP BY b.book_id, b.title ORDER BY borrow_count DESC LIMIT 10''')
        most_borrowed = cur.fetchall()
        
        cur.execute('''SELECT l.loan_id, b.title, m.first_name, m.last_name, l.due_date FROM loans l
                       JOIN books b ON l.book_id = b.book_id JOIN members m ON l.member_id = m.member_id
                       WHERE l.status='ACTIVE' AND l.due_date < %s ORDER BY l.due_date ASC''', (datetime.now().date(),))
        overdue = cur.fetchall()
        
        cur.close()
        conn.close()
        return render_template('reports.html', most_borrowed=most_borrowed, overdue=overdue)
    except Exception as e:
        return render_template('reports.html', most_borrowed=[], overdue=[])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
