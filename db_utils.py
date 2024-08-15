import sqlite3
import bcrypt

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    stored_password_hash = c.fetchone()
    conn.close()

    if stored_password_hash:
        stored_password_hash = stored_password_hash[0]
        return bcrypt.checkpw(password.encode(), stored_password_hash.encode())
    return False

def create_user(username, password):
    hashed_password = hash_password(password)
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError:
        raise ValueError("Username already exists")
    
def check_user_exists(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
    count = c.fetchone()[0]
    conn.close()
    return count > 0
