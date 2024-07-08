from flask import Flask, render_template, request, redirect, url_for, flash, session
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


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']
<<<<<<< HEAD
 
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM Users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
       
=======

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM Users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        
>>>>>>> 92aba5e30afe56d05b0a50ba28966a2fedc37348
        if user and check_password_hash(user[2], password):  # user[2] is the password_hash column
            session['user_id'] = user[0]
            session['role'] = user[4]  # Assuming role is in the 5th column (index 4)
            flash('Login successful!', 'success')
            cursor.close()
            return redirect(url_for('index'))  # Replace 'index' with your actual index route/function
        else:
            flash('Invalid credentials!', 'error')
            cursor.close()
            return redirect(url_for('login'))
 
    return render_template('login.html')


@app.route('/')
def index():
    return render_template('index.html')


# Decorator to check role
def role_required(role):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if 'role' in session and session['role'] == role:
                return fn(*args, **kwargs)
            flash(f'Unauthorized access for role "{role}".', 'danger')
            return redirect(url_for('index'))
        return decorated_view
    return wrapper
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_id = request.form['user_id']
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        role = request.form['role']
        email = request.form['email']
<<<<<<< HEAD
 
=======

>>>>>>> 92aba5e30afe56d05b0a50ba28966a2fedc37348
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO Users (user_id, username, password_hash, email, role) VALUES (%s, %s, %s, %s, %s)",
                       (user_id, username, hashed_password, email, role))
        mysql.connection.commit()
        cursor.close()
<<<<<<< HEAD
 
=======

>>>>>>> 92aba5e30afe56d05b0a50ba28966a2fedc37348
        flash('User registered successfully!', 'success')
        return redirect(url_for('login'))
 
    return render_template('register.html')

@app.route('/raise_ticket', methods=['GET', 'POST'])
@role_required(CLIENT_ROLE)
def raise_ticket():
    if request.method == 'POST':
        client_id = session['user_id']
        category_id = request.form['category_id']
        priority = request.form['priority']
        title = request.form['title']
        description = request.form['description']
        status_id = 1  # Default status for new tickets, which could be 'Open'
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO tickets (client_id, category_id, priority, title, description, status_id) VALUES (%s, %s, %s, %s, %s, %s)",
                       (client_id, category_id, priority, title, description, status_id))
        mysql.connection.commit()
        cursor.close()
        flash('Ticket raised successfully!', 'success')
        return redirect(url_for('view_tickets'))
 
    cursor = mysql.connection.cursor()
    
    cursor.execute("SELECT category_id, category_name FROM TicketCategories")
    categories = cursor.fetchall()
    print(categories)
    cursor.close()
    return render_template('raise_ticket.html', categories=categories)


@app.route('/view_tickets')
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
    return render_template('view_tickets.html', tickets=tickets)

@app.route('/manage_tickets')
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
    return render_template('manage_tickets.html', tickets=tickets, consultants=consultants)

@app.route('/assign_ticket/<int:ticket_id>', methods=['POST'])
@role_required(MANAGER_ROLE)
def assign_ticket(ticket_id):
    assigned_to = request.form['assigned_to']
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE tickets SET assigned_to = %s WHERE ticket_id = %s", (assigned_to, ticket_id))
    mysql.connection.commit()
    cursor.close()
    flash('Ticket assigned successfully!', 'success')
    return redirect(url_for('manage_tickets'))


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    flash('Logged out successfully!')
    return redirect(url_for('login'))

if __name__ == '__main__':
   app.run(debug = True)
