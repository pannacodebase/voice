import sqlite3
from flask import jsonify, request

def get_questions_by_category(category):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM questions WHERE category = ?', (category,))
    questions = c.fetchall()
    
    result = []
    
    for question in questions:
        q_data = {
            'id': question[0],
            'question': question[1],
            'category': question[2],
            'response_required': question[3],
            'question_type': question[4]
        }
        
        if q_data['question_type'] in [2, 3]:
            c.execute('SELECT * FROM question_options WHERE question_id = ?', (q_data['id'],))
            options = c.fetchall()
            q_data['options'] = [opt[2] for opt in options]
        
        result.append(q_data)
    
    conn.close()
    return result

def handle_submit_response(data):
    user_id = data.get('user_id')
    question_id = data.get('question_id')
    response = data.get('response')
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('INSERT INTO user_responses (user_id, question_id, response) VALUES (?, ?, ?)', (user_id, question_id, response))
    conn.commit()
    conn.close()
    
    return {'status': 'success'}
