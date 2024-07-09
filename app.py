from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# # Define role constants
# CLIENT_ROLE = 'client'
# MANAGER_ROLE = 'manager'
# CONSULTANT_ROLE = 'consultant'


# app = Flask(__name__)
# app.secret_key = 'asudsb'

# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = 'Sqlserver@123'
# app.config['MYSQL_DB'] = 'proj'

# mysql = MySQL(app)


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         user_id = request.form['user_id']
#         password = request.form['password']
#         cursor = mysql.connection.cursor()
#         cursor.execute("SELECT * FROM Users WHERE user_id = %s", (user_id,))
#         user = cursor.fetchone()
#         if user and check_password_hash(user[2], password):  # user[2] is the password_hash column
#             session['user_id'] = user[0]
#             session['role'] = user[4]  # Assuming role is in the 5th column (index 4)
#             flash('Login successful!', 'success')
#             cursor.close()
#             return redirect(url_for('index'))  # Replace 'index' with your actual index route/function
#         else:
#             flash('Invalid credentials!', 'error')
#             cursor.close()
#             return redirect(url_for('login'))
 
#     return render_template('login.html')


# @app.route('/')
# def index():
#     return render_template('index.html')


# # Decorator to check role
# def role_required(role):
#     def wrapper(fn):
#         @wraps(fn)
#         def decorated_view(*args, **kwargs):
#             if 'role' in session and session['role'] == role:
#                 return fn(*args, **kwargs)
#             flash(f'Unauthorized access for role "{role}".', 'danger')
#             return redirect(url_for('index'))
#         return decorated_view
#     return wrapper
# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         user_id = request.form['user_id']
#         username = request.form['username']
#         password = request.form['password']
#         hashed_password = generate_password_hash(password)
#         role = request.form['role']
#         email = request.form['email']
#         cursor = mysql.connection.cursor()
#         cursor.execute("INSERT INTO Users (user_id, username, password_hash, email, role) VALUES (%s, %s, %s, %s, %s)",
#                        (user_id, username, hashed_password, email, role))
#         mysql.connection.commit()
#         cursor.close()
#         flash('User registered successfully!', 'success')
#         return redirect(url_for('login'))
 
#     return render_template('register.html')

# @app.route('/raise_ticket', methods=['GET', 'POST'])
# @role_required(CLIENT_ROLE)
# def raise_ticket():
#     if request.method == 'POST':
#         client_id = session['user_id']
#         category_id = request.form['category_id']
#         priority = request.form['priority']
#         title = request.form['title']
#         description = request.form['description']
#         status_id = 1  # Default status for new tickets, which could be 'Open'
#         cursor = mysql.connection.cursor()
#         cursor.execute("INSERT INTO tickets (client_id, category_id, priority, title, description, status_id) VALUES (%s, %s, %s, %s, %s, %s)",
#                        (client_id, category_id, priority, title, description, status_id))
#         mysql.connection.commit()
#         cursor.close()
#         flash('Ticket raised successfully!', 'success')
#         return redirect(url_for('view_tickets'))
 
#     cursor = mysql.connection.cursor()
    
#     cursor.execute("SELECT category_id, category_name FROM TicketCategories")
#     categories = cursor.fetchall()
#     print(categories)
#     cursor.close()
#     return render_template('raise_ticket.html', categories=categories)


# @app.route('/view_tickets')
# @role_required(CLIENT_ROLE)
# def view_tickets():
#     client_id = session['user_id']
#     cursor = mysql.connection.cursor()
#     cursor.execute("SELECT t.ticket_id, tc.category_name, t.priority, t.title, t.description, ts.status_name FROM Tickets t "
#                    "JOIN TicketCategories tc ON t.category_id = tc.category_id "
#                    "JOIN TicketStatuses ts ON t.status_id = ts.status_id "
#                    "WHERE t.client_id = %s", (client_id,))
#     tickets = cursor.fetchall()
#     cursor.close()
#     return render_template('view_tickets.html', tickets=tickets)

# @app.route('/manage_tickets')
# @role_required(MANAGER_ROLE)
# def manage_tickets():
#     cursor = mysql.connection.cursor()
#     cursor.execute("SELECT t.ticket_id, t.client_id, u.username, tc.category_name, t.priority, t.title, t.description, ts.status_name, t.assigned_to FROM tickets t "
#                    "JOIN Users u ON t.client_id = u.user_id "
#                    "JOIN TicketCategories tc ON t.category_id = tc.category_id "
#                    "JOIN TicketStatuses ts ON t.status_id = ts.status_id")
#     tickets = cursor.fetchall()
#     cursor.execute("SELECT user_id, username FROM Users WHERE role = %s", (CONSULTANT_ROLE,))
#     consultants = cursor.fetchall()
#     cursor.close()
#     return render_template('manage_tickets.html', tickets=tickets, consultants=consultants)

# @app.route('/assign_ticket/<int:ticket_id>', methods=['POST'])
# @role_required(MANAGER_ROLE)
# def assign_ticket(ticket_id):
#     assigned_to = request.form['assigned_to']
#     cursor = mysql.connection.cursor()
#     cursor.execute("UPDATE tickets SET assigned_to = %s WHERE ticket_id = %s", (assigned_to, ticket_id))
#     mysql.connection.commit()
#     cursor.close()
#     flash('Ticket assigned successfully!', 'success')
#     return redirect(url_for('manage_tickets'))


# @app.route('/logout')
# def logout():
#     session.pop('user_id', None)
#     session.pop('role', None)
#     flash('Logged out successfully!')
#     return redirect(url_for('login'))

# if __name__ == '__main__':
#    app.run(debug = True)

from flask import Flask, request, jsonify, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# Define role constants
CLIENT_ROLE = 'client'
MANAGER_ROLE = 'manager'
CONSULTANT_ROLE = 'consultant'

app = Flask(__name__)
app.secret_key = 'asudsb'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'admin'
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
@role_required(CONSULTANT_ROLE)
def update_ticket_status(ticket_id):
    data = request.get_json()
    new_status = data.get('new_status', '').strip().lower()

    # Check if the new status is valid for consultants to update
    valid_statuses = ['verification', 'closed']
    if new_status not in valid_statuses:
        return jsonify({'message': f'Invalid status update for consultants! Valid statuses are: {", ".join(valid_statuses)}'}), 400

    # Check if the logged-in user is the consultant assigned to this ticket
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT assigned_to FROM tickets WHERE ticket_id = %s", (ticket_id,))
    ticket = cursor.fetchone()
    cursor.close()

    if not ticket:
        return jsonify({'message': 'Ticket not found!'}), 404

    assigned_to = ticket[0]

    if session.get('user_id') != assigned_to:
        return jsonify({'message': 'You are not authorized to update this ticket status!'}), 403

    # Update the ticket status
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE tickets SET status_id = (SELECT status_id FROM TicketStatuses WHERE status_name = %s) WHERE ticket_id = %s",
                   (new_status.capitalize(), ticket_id))  # capitalize the first letter of status_name
    mysql.connection.commit()
    cursor.close()

    return jsonify({'message': 'Ticket status updated successfully!'}), 200


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

