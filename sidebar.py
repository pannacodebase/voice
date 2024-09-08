import sqlite3

def get_users():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT id, name, picture FROM user')
    users = c.fetchall()
    conn.close()

    return [{'id': u[0], 'name': u[1], 'picture': u[2]} for u in users]
