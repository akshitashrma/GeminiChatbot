import sqlite3

def delete_user(username=None):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    if username:
        cursor.execute("DELETE FROM users WHERE username = ?", (username,))
        print(f"Deleted user: {username}")
    else:
        cursor.execute("DELETE FROM users")
        print("Deleted all users")
    
    conn.commit()
    conn.close()

# Example usage
# delete_user('Akshita Sharma')  # Delete a specific user
delete_user()  # Delete all users
