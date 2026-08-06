# Library Management System - Flask Web Application

A modern web-based Library Management System built with Flask and PostgreSQL, deployed on Railway.

## Features

- **📊 Dashboard** - View library statistics at a glance
- **📚 Books Management** - Add, edit, and manage books
- **👥 Members Management** - Manage library members
- **📋 Loans System** - Borrow and return books
- **💰 Fines Tracking** - Track outstanding fines
- **📈 Reports** - View analytics and overdue loans
- **🔐 Authentication** - Secure login system

## Tech Stack

- **Backend:** Python Flask
- **Database:** PostgreSQL
- **Hosting:** Railway
- **Frontend:** HTML, CSS, JavaScript

## Files Structure

```
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/
│   ├── base.html         # Base template with navigation
│   ├── login.html        # Login page
│   ├── dashboard.html    # Dashboard/Home
│   ├── books.html        # Books list
│   ├── add_book.html     # Add new book
│   ├── edit_book.html    # Edit book
│   ├── members.html      # Members list
│   ├── add_member.html   # Add new member
│   ├── edit_member.html  # Edit member
│   ├── loans.html        # Loans list
│   ├── borrow_book.html  # Create new loan
│   ├── fines.html        # Fines management
│   └── reports.html      # Analytics & reports
└── README.md             # This file
```

## Installation & Deployment

### Step 1: Create a GitHub Repository

1. Create a new repository on GitHub
2. Clone it locally
3. Copy all the files (app.py, requirements.txt, templates/) into the repo
4. Commit and push to GitHub

```bash
git add .
git commit -m "Initial commit: Library Management System"
git push origin main
```

### Step 2: Deploy to Railway

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub"
4. Connect your GitHub account
5. Select the repository you created
6. Click "Deploy"

### Step 3: Set Environment Variables

In Railway Dashboard:
1. Go to your project
2. Click on the service (app)
3. Click "Variables"
4. Add environment variable:
   - Name: `DATABASE_PUBLIC_URL`
   - Value: `postgresql://postgres:Library123@crossover.proxy.rlwy.net:59153/railway`

5. Go to "Settings" and generate a domain (e.g., `library-mgmt.railway.app`)

### Step 4: Access Your App

Once deployed, your app will be live at:
```
https://your-generated-domain.railway.app
```

## Demo Login Credentials

```
Username: admin1
Password: admin123
```

## Database Setup

The database should already be set up in Railway PostgreSQL with all tables created. If not, run the migration scripts first:

```sql
-- Create tables (see SQL schema in documentation)
```

## Usage

1. **Login** with demo credentials
2. **Dashboard** - View statistics and recent activity
3. **Books** - Manage book inventory
4. **Members** - Manage library members
5. **Loans** - Create loans (borrow books) and process returns
6. **Fines** - Track and mark fines as paid
7. **Reports** - View most borrowed books and overdue loans

## Features in Detail

### Books Management
- Add new books with ISBN, title, author, publisher, year, category
- Edit book information
- Track available copies vs. total copies
- View book status (AVAILABLE/OUT OF STOCK)

### Members Management
- Add new members with contact information
- Edit member details
- Track membership status (ACTIVE/SUSPENDED/EXPIRED)

### Loans System
- Create loans (borrow) with configurable loan period
- Automatically track due dates
- Return books and update inventory
- Flag overdue loans

### Fines Management
- Track fines for overdue books
- Mark fines as PENDING or PAID
- View all fines with member details

### Reports
- Most borrowed books ranking
- Overdue loans list with days overdue
- Member statistics
- Book circulation analytics

## Troubleshooting

### Can't connect to database?
- Verify the `DATABASE_PUBLIC_URL` environment variable is set correctly
- Check Railway PostgreSQL is online and accessible

### Login not working?
- Verify credentials (admin1/admin123)
- Check database has users table with sample data

### App won't start?
- Check `requirements.txt` is correct
- Verify Python version compatibility
- Check logs in Railway dashboard

## Future Enhancements

- Email notifications for overdue books
- QR code scanning for books
- Advanced search and filtering
- Reservation system
- Member payment processing
- SMS alerts
- Export reports to PDF

## Support

For issues or questions, check:
- Railway documentation: https://docs.railway.app
- Flask documentation: https://flask.palletsprojects.com
- PostgreSQL documentation: https://www.postgresql.org/docs

## License

This project is open source and available for educational purposes.
