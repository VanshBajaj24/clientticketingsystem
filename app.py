from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'asudsb'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Sqlserver@123'
app.config['MYSQL_DB'] = 'proj'

mysql = MySQL(app)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        #cursor.execute("SELECT * FROM users WHERE user_id = %s AND password = % s'", (user_id, password))
        cursor.execute("SELECT * FROM user WHERE user_id = %s AND password_hash = %s", (user_id, password))

        user = cursor.fetchone()
        cursor.close()
        if user:
            flash("here")
            session['user_id'] = user[0]
            session['role'] = user[2]
            flash('Login successful!','success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials!')
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
        password = generate_password_hash(request.form['password'])
        role = request.form['role']
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO users (user_id, password, role) VALUES (%s, %s, %s)", (user_id, password, role))
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