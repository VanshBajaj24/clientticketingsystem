from datetime import timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email_validator import validate_email, EmailNotValidError 
import smtplib
from flask import Flask, request, jsonify, redirect, url_for, flash, session, send_file,render_template
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import re
import csv
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import matplotlib
matplotlib.use('Agg')
import base64

CLIENT_ROLE = 'client'
MANAGER_ROLE = 'manager'
CONSULTANT_ROLE = 'consultant'

app = Flask(__name__)
app.secret_key = 'asudsb'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Sqlserver@123'
app.config['MYSQL_DB'] = 'proj'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config['SESSION_PERMANENT'] = True
 
SMTP_SERVER = 'smtp.gmail.com'  
SMTP_PORT = 587
SMTP_USER = 'bajajvansh01@gmail.com'  
SMTP_PASSWORD = 'sjdw jbjh eity rkvw'
 
mysql = MySQL(app)
 
def role_required(role):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if 'role' in session and session['role'] == role:
                return fn(*args, **kwargs)
            return jsonify({'message': f'Unauthorized access for role "{role}".'}), 403
        return decorated_view
    return wrapper
 
def send_email(subject, body, to_email):
    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = to_email
    msg['Subject'] = subject
 
    msg.attach(MIMEText(body, 'plain'))
 
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(SMTP_USER, to_email, text)
        server.quit()
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")

def log_ticket_action(ticket_id, user_id, action):
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO TicketLogs (ticket_id, user_id, action) VALUES (%s, %s, %s)",
                   (ticket_id, user_id, action))
    mysql.connection.commit()
    cursor.close()

def is_valid_email(email):
    try:
        validate_email(email)
        return True
    except EmailNotValidError as e:
        print(str(e))
        return False


class PasswordValidationException(Exception):
    pass
 
def is_valid_password(password):
    if len(password) < 6:
        raise PasswordValidationException("Password must be at least 6 characters long.")
    if not re.search(r"[a-z]", password):
        raise PasswordValidationException("Password must contain at least one lowercase letter.")
    if not re.search(r"[A-Z]", password):
        raise PasswordValidationException("Password must contain at least one uppercase letter.")
    if not re.search(r"\d", password):
        raise PasswordValidationException("Password must contain at least one digit.")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise PasswordValidationException("Password must contain at least one special character.")
    return True

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    # user_id = data['user_id']
    username = data['username']
    password = data['password']
    hashed_password = generate_password_hash(password)
    role = data['role']
    email = data['email']
    
    if not is_valid_email(email):
        return jsonify({'message': 'Invalid email format!'}), 400
    if not is_valid_password(password):
        return jsonify({'message': 'Invalid credentials!'}), 401
    
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO Users ( username, password_hash, email, role) VALUES ( %s, %s, %s, %s)",
                   ( username, hashed_password, email, role))
    mysql.connection.commit()
    cursor.close()
    return jsonify({'message': 'User registered successfully!'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user_id = data['user_id']
    password = data['password']
    
    
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Users WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()
    if user and check_password_hash(user[2], password):  
        session.permanent = True
        session['user_id'] = str(user[0])
        session['role'] = str(user[4]) 
        cursor.close()
        return jsonify({'message': 'Login successful!'}), 200
    else:
        cursor.close()
        return jsonify({'message': 'Invalid credentials!'}), 401
    
@app.route('/forgot_password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    user_id = data.get('user_id')
    email = data.get('email')
    new_password = data.get('new_password')
    
    if not user_id or not email or not new_password:
        return jsonify({'message': 'Missing user_id, email, or new_password in request!'}), 400
    
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Users WHERE user_id = %s AND email = %s", (user_id, email))
    user = cursor.fetchone()
    
    if user : 
        if not is_valid_password(new_password):
            cursor.close()
            return jsonify({'message': 'Invalid new password format! Password must be at least 8 characters long.'}), 400
        
        hashed_password = generate_password_hash(new_password)
        cursor.execute("UPDATE Users SET password_hash = %s WHERE user_id = %s", (hashed_password, user_id))
        mysql.connection.commit()
        cursor.close()
        return jsonify({'message': 'Password updated successfully!'}), 200
    else:
        cursor.close()
        return jsonify({'message': 'Invalid user_id, email, or old password!'}), 401

@app.route('/change_password', methods=['POST'])
def change_password():
    data = request.get_json()
    user_id = data.get('user_id')
    email = data.get('email')
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not user_id or not email or not old_password or not new_password:
        return jsonify({'message': 'Missing user_id, email, old_password, or new_password in request!'}), 400
    
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Users WHERE user_id = %s AND email = %s", (user_id, email))
    user = cursor.fetchone()
    
    if user and check_password_hash(user[2], old_password): 
        if not is_valid_password(new_password):
            cursor.close()
            return jsonify({'message': 'Invalid new password format! Password must be at least 8 characters long.'}), 400
        
        hashed_password = generate_password_hash(new_password)
        cursor.execute("UPDATE Users SET password_hash = %s WHERE user_id = %s", (hashed_password, user_id))
        mysql.connection.commit()
        cursor.close()
        return jsonify({'message': 'Password updated successfully!'}), 200
    else:
        cursor.close()
        return jsonify({'message': 'Invalid user_id, email, or old password!'}), 401


@app.route('/raise_ticket', methods=['POST'])
@role_required(CLIENT_ROLE)
def raise_ticket():
    data = request.get_json()
    client_id = session['user_id']
    category_id = data['category_id']
    priority = data['priority']
    title = data['title']
    description = data['description']
    status_id = 1 
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO tickets (client_id, category_id, priority, title, description, status_id) VALUES (%s, %s, %s, %s, %s, %s)",
                   (client_id, category_id, priority, title, description, status_id))
    ticket_id = cursor.lastrowid
    mysql.connection.commit()
    log_ticket_action(ticket_id, client_id, 'Ticket Raised')
    cursor.execute("SELECT email FROM Users WHERE user_id = %s", (client_id,))
    email = cursor.fetchone()[0]
    cursor.close()
    
    if is_valid_email(email):
        send_email("Ticket Raised Successfully", f"Your ticket with ID {ticket_id} has been raised successfully.", email)
    cursor.close()
    return jsonify({'message': 'Ticket raised successfully!'}), 201

@app.route('/view_tickets', methods=['GET'])
@role_required(CLIENT_ROLE)
def view_tickets():
    client_id = session['user_id']
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT t.ticket_id, tc.category_name, t.priority, t.title, t.description, ts.status_name FROM Tickets t "
                   "JOIN TicketCategories tc ON t.category_id = tc.category_id "
                   "JOIN TicketStatuses ts ON t.status_id = ts.status_id "
                   "WHERE t.client_id = %s", (client_id,))
    tickets = cursor.fetchall()
    cursor.close()
    return jsonify(tickets), 200

@app.route('/recent_first', methods=['GET'])
@role_required(CLIENT_ROLE)
def recent_first():
    client_id = session['user_id']
    
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT t.ticket_id, tc.category_name, t.priority, t.title, t.description, ts.status_name, t.created_at, t.updated_at "
                   "FROM Tickets t "
                   "JOIN TicketCategories tc ON t.category_id = tc.category_id "
                   "JOIN TicketStatuses ts ON t.status_id = ts.status_id "
                   "WHERE t.client_id = %s "
                   "ORDER BY t.created_at DESC", (client_id,))
    tickets = cursor.fetchall()
    cursor.close()

    if not tickets:
        return jsonify({'message': 'No tickets found for the client!'}), 404

    ticket_list = []
    for ticket in tickets:
        ticket_dict = {
            'ticket_id': ticket[0],
            'category_name': ticket[1],
            'priority': ticket[2],
            'title': ticket[3],
            'description': ticket[4],
            'status_name': ticket[5],
            'created_at': ticket[6],
            'updated_at': ticket[7]
        }
        ticket_list.append(ticket_dict)

    return jsonify(ticket_list)


@app.route('/manage_tickets', methods=['GET'])
@role_required(MANAGER_ROLE)
def manage_tickets():
    cursor = mysql.connection.cursor()
    
    cursor.execute(
        "SELECT t.ticket_id, t.client_id, u.username, tc.category_name, t.priority, t.title, t.description, ts.status_name, t.assigned_to "
        "FROM tickets t "
        "JOIN Users u ON t.client_id = u.user_id "
        "JOIN TicketCategories tc ON t.category_id = tc.category_id "
        "JOIN TicketStatuses ts ON t.status_id = ts.status_id ORDER BY t.ticket_id"
    )
    tickets = cursor.fetchall()
    cursor.execute(
        "SELECT u.user_id, u.username, COUNT(t.ticket_id) as assigned_ticket_count "
        "FROM Users u "
        "LEFT JOIN tickets t ON u.user_id = t.assigned_to AND t.status_id = %s "
        "WHERE u.role = %s "
        "GROUP BY u.user_id, u.username",
        (2, CONSULTANT_ROLE)
    )
    consultants = cursor.fetchall()
    
    cursor.close()
    
    return jsonify({'tickets': tickets, 'consultants': consultants}), 200

@app.route('/manage_tickets/<status_name>', methods=['GET'])
@role_required(MANAGER_ROLE)
def manage_tickets_by_status(status_name):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT t.ticket_id, t.client_id, u.username, tc.category_name, t.priority, t.title, t.description, ts.status_name, t.assigned_to FROM tickets t "
                   "JOIN Users u ON t.client_id = u.user_id "
                   "JOIN TicketCategories tc ON t.category_id = tc.category_id "
                   "JOIN TicketStatuses ts ON t.status_id = ts.status_id "
                   "WHERE ts.status_name = %s", (status_name,))
    tickets = cursor.fetchall()
    cursor.close()
    return jsonify({'tickets': tickets}), 200

@app.route('/assign_ticket/<int:ticket_id>', methods=['POST'])
@role_required(MANAGER_ROLE)
def assign_ticket(ticket_id):
    data = request.get_json()
    assigned_to = data['assigned_to']
    
    cursor = mysql.connection.cursor()
    
    cursor.execute("SELECT role FROM users WHERE user_id = %s", (assigned_to,))
    result = cursor.fetchone()
    
    if result and result[0] == 'consultant':
        status_assigned = 2
        cursor.execute("UPDATE tickets SET assigned_to = %s, status_id = %s WHERE ticket_id = %s", (assigned_to, status_assigned, ticket_id))
        mysql.connection.commit()
        log_ticket_action(ticket_id, session['user_id'], f'Ticket Assigned to {assigned_to}')
        cursor.close()
        return jsonify({'message': 'Ticket assigned successfully!'}), 200
    else:
        cursor.close()
        return jsonify({'error': 'Ticket can only be assigned to a consultant!'}), 403


@app.route('/ticket_logs', methods=['GET'])
@role_required(MANAGER_ROLE)
def ticket_logs():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT tl.log_id, tl.ticket_id, tl.user_id, u.username, tl.action, tl.timestamp FROM TicketLogs tl "
                   "JOIN Users u ON tl.user_id = u.user_id")
    logs = cursor.fetchall()
    cursor.close()
    return jsonify({'logs': logs}), 200

@app.route('/update_ticket_status/<int:ticket_id>', methods=['POST'])
def update_ticket_status(ticket_id):
    if 'role' not in session or 'user_id' not in session:
        return jsonify({'message': 'Unauthorized access!'}), 403

    user_role = session['role']
    user_id = session['user_id']

    if user_role == CONSULTANT_ROLE:
        new_status = 'Verification '
    elif user_role == MANAGER_ROLE:
        new_status = 'Closed'
    else:
        return jsonify({'message': 'Unauthorized access!'}), 403

    if user_role == CONSULTANT_ROLE:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT assigned_to FROM tickets WHERE ticket_id = %s", (ticket_id,))
        ticket = cursor.fetchone()

        if not ticket:
            cursor.close()
            return jsonify({'message': 'Ticket not found!'}), 404

        assigned_to = ticket[0]
           
        cursor.close()

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT status_id FROM TicketStatuses WHERE LOWER(status_name) = %s", (new_status.lower(),))
    status = cursor.fetchone()
    cursor.close()

    if not status:
        return jsonify({'message': 'Invalid status name!'}), 400

    status_id = status[0]
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE tickets SET status_id = %s WHERE ticket_id = %s", (status_id, ticket_id))
    mysql.connection.commit()
    
    cursor.execute("SELECT client_id FROM tickets WHERE ticket_id = %s", (ticket_id,))
    client_id = cursor.fetchone()[0]
    
    cursor.execute("SELECT email FROM Users WHERE user_id = %s", (client_id,))
    email = cursor.fetchone()[0]
    cursor.close()
    # Log ticket action
    log_ticket_action(ticket_id, user_id, f'Ticket status updated to {new_status}')
    if new_status == 'Closed' and is_valid_email(email):
        send_email("Ticket Resolved", f"Your ticket with ID {ticket_id} has been resolved.", email)

    return jsonify({'message': f'Ticket status updated to {new_status} successfully!'}), 200
@app.route('/export_tickets', methods=['GET'])
@role_required(MANAGER_ROLE)
def export_tickets():
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT t.ticket_id, t.client_id, u.username, tc.category_name, t.priority, t.title, t.description,
               ts.status_name, t.assigned_to, t.created_at, t.updated_at,
               (SELECT u2.username FROM Users u2 WHERE u2.user_id = t.assigned_to) as assigned_to_name
        FROM tickets t
        JOIN Users u ON t.client_id = u.user_id
        JOIN TicketCategories tc ON t.category_id = tc.category_id
        JOIN TicketStatuses ts ON t.status_id = ts.status_id
        WHERE t.created_at >= NOW() - INTERVAL 6 MONTH
    """)
    tickets = cursor.fetchall()
    cursor.close()
   
    csv_file_path = 'tickets.csv'
   
    with open(csv_file_path, 'w', newline='') as csvfile:
        fieldnames = ['ticket_id', 'client_id', 'username', 'category_name', 'priority', 'title', 'description', 'status_name', 'assigned_to', 'assigned_to_name', 'created_at', 'updated_at']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
       
        writer.writeheader()
        for ticket in tickets:
            writer.writerow({
                'ticket_id': ticket[0],
                'client_id': ticket[1],
                'username': ticket[2],
                'category_name': ticket[3],
                'priority': ticket[4],
                'title': ticket[5],
                'description': ticket[6],
                'status_name': ticket[7],
                'assigned_to': ticket[8],
                'created_at': ticket[9],
                'updated_at': ticket[10],
                'assigned_to_name': ticket[11]
            })
   
    return send_file(csv_file_path, as_attachment=True)

@app.route('/generate_reports', methods=['GET'])
@role_required(MANAGER_ROLE)
def generate_reports():
    query = "SELECT role, COUNT(*) as count FROM Users GROUP BY role"
    user_roles_counts_df = pd.read_sql(query, mysql.connection, index_col='role')
 
    df = pd.read_csv('tickets.csv')
 
    priority_mapping = {'High': 3, 'Medium': 2, 'Low': 1}
    df['priority'] = df['priority'].map(priority_mapping)
 
    status_counts = df['status_name'].value_counts()
 
    average_priority_by_category = df.groupby('category_name')['priority'].mean()
 
    assigned_to_counts = df['assigned_to'].value_counts()
 
    df['created_at'] = pd.to_datetime(df['created_at'])
    tickets_over_time = df['created_at'].dt.date.value_counts().sort_index()
 
    df['updated_at'] = pd.to_datetime(df['updated_at'])
    closed_tickets = df[df['status_name'] == 'Closed']
    closed_tickets_over_time = closed_tickets['updated_at'].dt.date.value_counts().sort_index()

    df_last_6_months = df[df['created_at'] >= (pd.Timestamp.now() - pd.DateOffset(months=6))]
    tickets_by_client = df_last_6_months['client_id'].value_counts(normalize=True) * 100
 
    plots = []
 
    # Plot Count of Tickets by Status
    plt.figure(figsize=(10, 6))
    ax = status_counts.plot(kind='bar', color='skyblue')
    plt.title('Count of Tickets by Status')
    plt.xlabel('Status')
    plt.ylabel('Count')
    plt.xticks(rotation=45)

    for i in ax.containers:
        ax.bar_label(i,)
    plt.tight_layout()
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plots.append(base64.b64encode(img.getvalue()).decode('utf8'))
    plt.close()
 
    # Plot Average Ticket Priority by Category
    plt.figure(figsize=(10, 6))
    ax = average_priority_by_category.plot(kind='bar', color='green')
    plt.title('Average Ticket Priority by Category')
    plt.xlabel('Category')
    plt.ylabel('Average Priority')
    plt.xticks(rotation=45)
    for i in ax.containers:
        ax.bar_label(i,)
    plt.tight_layout()
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plots.append(base64.b64encode(img.getvalue()).decode('utf8'))
    plt.close()
 
    # Bar chart of count of tickets by assigned consultant
    plt.figure(figsize=(10, 6))
    ax = assigned_to_counts.plot(kind='bar', color='purple')
    plt.title('Count of Tickets by Assigned Consultant')
    plt.xlabel('Consultant')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    for i in ax.containers:
        ax.bar_label(i,)
    plt.tight_layout()
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plots.append(base64.b64encode(img.getvalue()).decode('utf8'))
    plt.close()
 
    # Line chart of tickets over time
    plt.figure(figsize=(10, 6))
    ax = tickets_over_time.plot(kind='line', color='orange', marker='o')
    plt.title('Tickets Over Time')
    plt.xlabel('Date')
    plt.ylabel('Count')
    plt.grid(True)
    plt.tight_layout()
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plots.append(base64.b64encode(img.getvalue()).decode('utf8'))
    plt.close()

    # Plot the percentage of tickets raised by different clients in the last 6 months
    plt.figure(figsize=(10, 6))
    ax = tickets_by_client.plot(kind='bar', color='blue')
    plt.title('Percentage of Tickets Raised by Clients in Last 6 Months')
    plt.xlabel('Client ID')
    plt.ylabel('Percentage')
    plt.xticks(rotation=45)
    for i in ax.containers:
        ax.bar_label(i, fmt='%.1f%%')
    plt.tight_layout()
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plots.append(base64.b64encode(img.getvalue()).decode('utf8'))
    plt.close()

    # Pie chart of user roles
    plt.figure(figsize=(10, 6))
    user_roles_counts_df['count'].plot(kind='pie', autopct='%1.1f%%', colors=['red', 'blue', 'yellow'], startangle=140)
    plt.title('User Roles Distribution')
    plt.ylabel('')  
    plt.tight_layout()
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plots.append(base64.b64encode(img.getvalue()).decode('utf8'))
    plt.close()
 
    # Bar chart of closed tickets over time with at least 10 dates and y-axis limit of at least 10
    if len(closed_tickets_over_time) < 10:
        min_date = closed_tickets_over_time.index.min()
        max_date = closed_tickets_over_time.index.max()
        all_dates = pd.date_range(start=min_date, end=max_date + pd.Timedelta(days=10 - len(closed_tickets_over_time)))
        closed_tickets_over_time = closed_tickets_over_time.reindex(all_dates, fill_value=0)
 
    plt.figure(figsize=(10, 6))
    ax = closed_tickets_over_time.plot(kind='bar', color='red', width=0.5)
    plt.title('Closed Tickets Over Time')
    plt.xlabel('Date')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.ylim(0, max(10, closed_tickets_over_time.max() + 1))
    plt.tight_layout()
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plots.append(base64.b64encode(img.getvalue()).decode('utf8'))
    plt.close()
 
    return render_template('plots.html', plots=plots)
        
@app.route('/consultant_tickets', methods=['GET'])
@role_required(CONSULTANT_ROLE)
def consultant_tickets():
    consultant_id = session.get('user_id')

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT t.ticket_id, tc.category_name, t.priority, t.title, t.description, ts.status_name "
                   "FROM tickets t "
                   "JOIN TicketCategories tc ON t.category_id = tc.category_id "
                   "JOIN TicketStatuses ts ON t.status_id = ts.status_id "
                   "WHERE t.assigned_to = %s", (consultant_id,))
    tickets = cursor.fetchall()
    cursor.close()

    ticket_list = []
    for ticket in tickets:
        ticket_dict = {
            'ticket_id': ticket[0],
            'category_name': ticket[1],
            'priority': ticket[2],
            'title': ticket[3],
            'description': ticket[4],
            'status_name': ticket[5]
        }
        ticket_list.append(ticket_dict)

    return jsonify({'tickets': ticket_list}), 200

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    return jsonify({'message': 'Logged out successfully!'}), 200


if __name__ == '__main__':
    app.run(debug=True)
