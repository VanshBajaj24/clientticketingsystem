from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

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

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM Users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        
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

@app.route('/manage_users')
def manage_users():
    return render_template('manage_users.html')

@app.route('/manage_tickets')
def manage_tickets():
    return render_template('manage_tickets.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_id = request.form['user_id']
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        role = request.form['role']
        email = request.form['email']

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO Users (user_id, username, password_hash, email, role) VALUES (%s, %s, %s, %s, %s)",
                       (user_id, username, hashed_password, email, role))
        mysql.connection.commit()
        cursor.close()

        flash('User registered successfully!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    flash('Logged out successfully!')
    return redirect(url_for('login'))

if __name__ == '__main__':
   app.run(debug = True)
