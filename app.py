from flask import Flask, request, jsonify, redirect, url_for, flash, session, send_file
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import csv
import os
# Define role constants
CLIENT_ROLE = 'client'
MANAGER_ROLE = 'manager'
CONSULTANT_ROLE = 'consultant'

app = Flask(__name__)
app.secret_key = 'asudsb'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Sqlserver@123'
app.config['MYSQL_DB'] = 'proj'

mysql = MySQL(app)

# Decorator to check role
def role_required(role):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if 'role' in session and session['role'] == role:
                return fn(*args, **kwargs)
            return jsonify({'message': f'Unauthorized access for role "{role}".'}), 403
        return decorated_view
    return wrapper

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user_id = data['user_id']
    password = data['password']
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Users WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()
    if user and check_password_hash(user[2], password):  # user[2] is the password_hash column
        session['user_id'] = user[0]
        session['role'] = user[4]  # Assuming role is in the 5th column (index 4)
        cursor.close()
        return jsonify({'message': 'Login successful!'}), 200
    else:
        cursor.close()
        return jsonify({'message': 'Invalid credentials!'}), 401

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    user_id = data['user_id']
    username = data['username']
    password = data['password']
    hashed_password = generate_password_hash(password)
    role = data['role']
    email = data['email']
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO Users (user_id, username, password_hash, email, role) VALUES (%s, %s, %s, %s, %s)",
                   (user_id, username, hashed_password, email, role))
    mysql.connection.commit()
    cursor.close()
    return jsonify({'message': 'User registered successfully!'}), 201

@app.route('/raise_ticket', methods=['POST'])
@role_required(CLIENT_ROLE)
def raise_ticket():
    data = request.get_json()
    client_id = session['user_id']
    category_id = data['category_id']
    priority = data['priority']
    title = data['title']
    description = data['description']
    status_id = 1  # Default status for new tickets, which could be 'Open'
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO tickets (client_id, category_id, priority, title, description, status_id) VALUES (%s, %s, %s, %s, %s, %s)",
                   (client_id, category_id, priority, title, description, status_id))
    mysql.connection.commit()
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

@app.route('/manage_tickets', methods=['GET'])
@role_required(MANAGER_ROLE)
def manage_tickets():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT t.ticket_id, t.client_id, u.username, tc.category_name, t.priority, t.title, t.description, ts.status_name, t.assigned_to FROM tickets t "
                   "JOIN Users u ON t.client_id = u.user_id "
                   "JOIN TicketCategories tc ON t.category_id = tc.category_id "
                   "JOIN TicketStatuses ts ON t.status_id = ts.status_id")
    tickets = cursor.fetchall()
    cursor.execute("SELECT user_id, username FROM Users WHERE role = %s", (CONSULTANT_ROLE,))
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
    status_assigned = 2 
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE tickets SET assigned_to = %s, status_id = %s WHERE ticket_id = %s", (assigned_to, status_assigned, ticket_id))
    mysql.connection.commit()
    cursor.close()
    return jsonify({'message': 'Ticket assigned successfully!'}), 200

    
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

    # Check if the logged-in user is the consultant assigned to this ticket (if consultant)
    if user_role == CONSULTANT_ROLE:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT assigned_to FROM tickets WHERE ticket_id = %s", (ticket_id,))
        ticket = cursor.fetchone()

        if not ticket:
            cursor.close()
            return jsonify({'message': 'Ticket not found!'}), 404

        assigned_to = ticket[0]

        if user_id != assigned_to:
            cursor.close()
            return jsonify({'message': 'You are not authorized to update this ticket status!'}), 403

        cursor.close()

    # Retrieve the status_id from TicketStatuses table
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT status_id FROM TicketStatuses WHERE LOWER(status_name) = %s", (new_status.lower(),))
    status = cursor.fetchone()
    cursor.close()

    if not status:
        return jsonify({'message': 'Invalid status name!'}), 400

    status_id = status[0]

    # Update the ticket status
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE tickets SET status_id = %s WHERE ticket_id = %s", (status_id, ticket_id))
    mysql.connection.commit()
    cursor.close()

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

@app.route('/consultant_tickets', methods=['GET'])
@role_required(CONSULTANT_ROLE)
def consultant_tickets():
    consultant_id = session.get('user_id')

    # Fetch tickets assigned to the consultant from the database
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT t.ticket_id, tc.category_name, t.priority, t.title, t.description, ts.status_name "
                   "FROM tickets t "
                   "JOIN TicketCategories tc ON t.category_id = tc.category_id "
                   "JOIN TicketStatuses ts ON t.status_id = ts.status_id "
                   "WHERE t.assigned_to = %s", (consultant_id,))
    tickets = cursor.fetchall()
    cursor.close()

    # Prepare JSON response
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

