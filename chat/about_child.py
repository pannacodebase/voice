import sqlite3

def get_questions():
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT question FROM chat_questions WHERE category = ?', ('about_child',))
        questions = c.fetchall()
        conn.close()
        
        return [q[0] for q in questions]
    except Exception as e:
        print(f"Error fetching questions: {e}")
        return []
