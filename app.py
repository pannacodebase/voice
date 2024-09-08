import sqlite3
import json
from flask import Flask, jsonify, redirect, render_template, session, url_for, abort
import requests
from authlib.integrations.flask_client import OAuth
from chat.chat_interface import get_questions_by_category


# Function to fetch configuration values from the database
def get_config_value(key):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT value FROM config WHERE key = ?', (key,))
    value = c.fetchone()
    conn.close()
    if value:
        return value[0]
    else:
        raise ValueError(f"Configuration key '{key}' not found in the database")

# Initialize Flask app
app = Flask(__name__)

# Fetch configuration values from the database
appConf = {
    "OAUTH2_CLIENT_ID": get_config_value('OAUTH2_CLIENT_ID'),
    "OAUTH2_CLIENT_SECRET": get_config_value('OAUTH2_CLIENT_SECRET'),
    "OAUTH2_META_URL": get_config_value('OAUTH2_META_URL'),
    "FLASK_SECRET": get_config_value('FLASK_SECRET'),
    "FLASK_PORT": int(get_config_value('FLASK_PORT') or 5000)  # Default port is 5000 if not found
}

app.secret_key = appConf.get("FLASK_SECRET") or 'supersecretkey'

# Set up OAuth
oauth = OAuth(app)
oauth.register(
    "google",
    client_id=appConf.get("OAUTH2_CLIENT_ID"),
    client_secret=appConf.get("OAUTH2_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email https://www.googleapis.com/auth/user.birthday.read https://www.googleapis.com/auth/user.gender.read",
    },
    server_metadata_url=f'{appConf.get("OAUTH2_META_URL")}',
)

# Create the SQLite database and tables
def create_database():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Create config table if not exists
    c.execute('''
        CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')

    # Create user table
    c.execute('''
        CREATE TABLE IF NOT EXISTS user (
            id TEXT PRIMARY KEY,
            email TEXT,
            name TEXT,
            picture TEXT,
            gender TEXT,
            birthdate TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Save user information to the database
def save_user_to_db(user_info):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    user_id = user_info['userinfo']['sub']
    email = user_info['userinfo'].get('email', '')
    name = user_info['userinfo'].get('name', '')
    picture = user_info['userinfo'].get('picture', '')

    # Handle optional fields (gender and birthdate)
    gender = None
    birthdate = None
    if 'personData' in user_info:
        person_data = user_info['personData']
        if 'genders' in person_data and person_data['genders']:
            gender = person_data['genders'][0].get('formattedValue', '')
        if 'birthdays' in person_data and person_data['birthdays']:
            bday = person_data['birthdays'][0]['date']
            birthdate = f"{bday.get('year', '')}-{bday.get('month', ''):02d}-{bday.get('day', ''):02d}"

    c.execute('''
        INSERT OR REPLACE INTO user (id, email, name, picture, gender, birthdate)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, email, name, picture, gender, birthdate))

    conn.commit()
    conn.close()

# Routes
@app.route("/")
def home():
    user = session.get("user")
    return render_template("home.html", session=session, user=user)

@app.route("/signin-google")
def googleCallback():
    token = oauth.google.authorize_access_token()
    personDataUrl = "https://people.googleapis.com/v1/people/me?personFields=genders,birthdays"
    personData = requests.get(personDataUrl, headers={
        "Authorization": f"Bearer {token['access_token']}"
    }).json()
    token["personData"] = personData
    session["user"] = token
    save_user_to_db(token)
    return redirect(url_for("main"))

@app.route("/main")
def main():
    user = session.get("user")
    if not user:
        return redirect(url_for("home"))
    return render_template("main.html", user=user)

@app.route("/google-login")
def googleLogin():
    if "user" in session:
        abort(404)
    return oauth.google.authorize_redirect(redirect_uri=url_for("googleCallback", _external=True))

@app.route("/questions/<category>")
def get_questions(category):
    try:
        questions = get_questions_by_category(category)
        return jsonify([{'question': q} for q in questions])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))

if __name__ == "__main__":
    create_database()
    app.run(host="0.0.0.0", port=appConf.get("FLASK_PORT"), debug=True)
