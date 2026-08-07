<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Library Management System{% endblock %}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f5f5f5;
            color: #333;
        }
        
        .navbar {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .navbar h1 {
            font-size: 1.5rem;
            font-weight: 600;
        }
        
        .navbar a {
            color: white;
            text-decoration: none;
            margin-left: 2rem;
            font-size: 0.95rem;
            transition: opacity 0.3s;
        }
        
        .navbar a:hover {
            opacity: 0.8;
        }
        
        .container {
            display: flex;
            min-height: calc(100vh - 70px);
        }
        
        .sidebar {
            width: 250px;
            background-color: #2c3e50;
            color: white;
            padding: 2rem 0;
            box-shadow: 2px 0 4px rgba(0,0,0,0.1);
        }
        
        .sidebar a {
            display: block;
            padding: 1rem 1.5rem;
            color: #ecf0f1;
            text-decoration: none;
            border-left: 3px solid transparent;
            transition: all 0.3s;
        }
        
        .sidebar a:hover,
        .sidebar a.active {
            background-color: #34495e;
            border-left-color: #3498db;
            color: white;
        }
        
        .main-content {
            flex: 1;
            padding: 2rem;
            overflow-y: auto;
        }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 2px solid #ecf0f1;
        }
        
        .header h2 {
            font-size: 1.8rem;
            color: #2c3e50;
        }
        
        .user-info {
            background-color: white;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            font-size: 0.9rem;
            color: #666;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .stat-card {
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }
        
        .stat-card h3 {
            color: #666;
            font-size: 0.85rem;
            text-transform: uppercase;
            margin-bottom: 0.5rem;
        }
        
        .stat-card .number {
            font-size: 2rem;
            font-weight: bold;
            color: #2c3e50;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-top: 1rem;
        }
        
        thead {
            background-color: #34495e;
            color: white;
        }
        
        th {
            padding: 1rem;
            text-align: left;
            font-weight: 600;
        }
        
        td {
            padding: 0.75rem 1rem;
            border-bottom: 1px solid #ecf0f1;
        }
        
        tbody tr:hover {
            background-color: #f9f9f9;
        }
        
        .btn {
            display: inline-block;
            padding: 0.5rem 1rem;
            background-color: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            border: none;
            cursor: pointer;
            font-size: 0.9rem;
            transition: background-color 0.3s;
        }
        
        .btn:hover {
            background-color: #764ba2;
        }
        
        .btn-danger {
            background-color: #e74c3c;
        }
        
        .btn-danger:hover {
            background-color: #c0392b;
        }
        
        .btn-small {
            padding: 0.35rem 0.75rem;
            font-size: 0.8rem;
        }
        
        .alert {
            padding: 1rem;
            border-radius: 4px;
            margin-bottom: 1rem;
        }
        
        .alert-error {
            background-color: #f8d7da;
            color: #721c24;
            border-left: 4px solid #f5c6cb;
        }
        
        .alert-success {
            background-color: #d4edda;
            color: #155724;
            border-left: 4px solid #c3e6cb;
        }
        
        .empty-state {
            text-align: center;
            padding: 2rem;
            color: #999;
        }
        
        .empty-state p {
            margin-top: 1rem;
        }
        
        @media (max-width: 768px) {
            .container {
                flex-direction: column;
            }
            
            .sidebar {
                width: 100%;
                display: flex;
                overflow-x: auto;
                padding: 1rem 0;
            }
            
            .sidebar a {
                flex: 0 0 auto;
                border-left: none;
                border-bottom: 3px solid transparent;
                padding: 0.75rem 1rem;
            }
            
            .sidebar a:hover,
            .sidebar a.active {
                border-left: none;
                border-bottom-color: #3498db;
            }
        }
    </style>
</head>
<body>
    <div class="navbar">
        <h1>📚 Library Management System</h1>
        <div>
            {% if session.get('username') %}
                <span>Welcome, <strong>{{ session.get('username') }}</strong></span>
                <a href="/logout">Logout</a>
            {% endif %}
        </div>
    </div>
    
    <div class="container">
        {% if session.get('username') %}
        <div class="sidebar">
            <a href="/dashboard" class="{% if request.path == '/dashboard' %}active{% endif %}">📊 Dashboard</a>
            <a href="/books" class="{% if request.path == '/books' %}active{% endif %}">📖 Books</a>
            <a href="/members" class="{% if request.path == '/members' %}active{% endif %}">👥 Members</a>
            <a href="/loans" class="{% if request.path == '/loans' %}active{% endif %}">📋 Loans</a>
            <a href="/fines" class="{% if request.path == '/fines' %}active{% endif %}">💰 Fines</a>
            <a href="/reports" class="{% if request.path == '/reports' %}active{% endif %}">📈 Reports</a>
        </div>
        {% endif %}
        
        <div class="main-content">
            {% if error %}
                <div class="alert alert-error">
                    <strong>Error:</strong> {{ error }}
                </div>
            {% endif %}
            
            {% block content %}{% endblock %}
        </div>
    </div>
</body>
</html>
