import json
import mysql.connector
from werkzeug.security import generate_password_hash
 
 
 
def insert_users(users):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Sqlserver@123",
        database="proj"
    )
    cursor = conn.cursor()
 
    for user in users:
        username = user['username']
        password = user['password']
        hashed_password = generate_password_hash(password)
        role = user['role']
        email = user['email']
        cursor.execute("INSERT INTO Users (username, password_hash, email, role) VALUES (%s, %s, %s, %s)",
                       (username, hashed_password, email, role))
 
    conn.commit()
    cursor.close()
    conn.close()
 
if __name__ == "__main__":
    with open('users.json') as f:
        users = json.load(f)
    insert_users(users)
 