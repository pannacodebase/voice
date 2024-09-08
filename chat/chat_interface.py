import sqlite3
from .about_child import get_questions as get_about_child_questions
from .therapies import get_questions as get_therapies_questions
from .policies import get_questions as get_policies_questions
from .local_laws import get_questions as get_local_laws_questions
from .learning_resources import get_questions as get_learning_resources_questions

def get_questions_by_category(category):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT question FROM questions WHERE category = ?', (category,))
    questions = [row[0] for row in c.fetchall()]
    conn.close()
    return questions
