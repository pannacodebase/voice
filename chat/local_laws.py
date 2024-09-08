import sqlite3

def get_questions():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT question FROM chat_questions WHERE category = ?', ('local_laws',))
    questions = c.fetchall()
    conn.close()
    
    return [q[0] for q in questions]
