import sqlite3
import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Tworzenie bazy danych
def init_db():
    conn = sqlite3.connect('billiard_tracker.db')
    c = conn.cursor()
    
    # Tabela użytkowników
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nickname TEXT UNIQUE NOT NULL,
            profile_image TEXT
        )
    ''')
    
    # Tabela gier
    c.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player1 TEXT NOT NULL,
            player2 TEXT NOT NULL,
            winner TEXT NOT NULL
        )
    ''')
    
    # Tabela piw
    c.execute('''
        CREATE TABLE IF NOT EXISTS beers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER NOT NULL,
            player TEXT NOT NULL,
            beer_count INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (game_id) REFERENCES games (id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

# Logowanie/Rejestracja użytkownika
@app.route('/login', methods=['POST'])
def login():
    nickname = request.form['nickname']
    profile_image = request.files.get('profile_image')

    conn = sqlite3.connect('billiard_tracker.db')
    c = conn.cursor()
    
    # Sprawdź, czy użytkownik istnieje
    c.execute('SELECT * FROM users WHERE nickname = ?', (nickname,))
    user = c.fetchone()
    
    if not user:
        image_filename = None
        if profile_image:
            image_filename = secure_filename(profile_image.filename)
            profile_image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
        
        c.execute('INSERT INTO users (nickname, profile_image) VALUES (?, ?)', (nickname, image_filename))
        conn.commit()
    
    conn.close()
    return redirect(url_for('index'))

# Pobierz dane użytkownika
@app.route('/get_user/<nickname>', methods=['GET'])
def get_user(nickname):
    conn = sqlite3.connect('billiard_tracker.db')
    c = conn.cursor()
    c.execute('SELECT nickname, profile_image FROM users WHERE nickname = ?', (nickname,))
    user = c.fetchone()
    conn.close()
    
    if user:
        return jsonify({"nickname": user[0], "profile_image": user[1]})
    return jsonify({"error": "User not found"}), 404

# Wyświetl listę gier
@app.route('/get_games', methods=['GET'])
def get_games():
    conn = sqlite3.connect('billiard_tracker.db')
    c = conn.cursor()
    c.execute('''
        SELECT g.id, g.player1, g.player2, g.winner, b.player, b.beer_count
        FROM games g
        JOIN beers b ON g.id = b.game_id
    ''')
    rows = c.fetchall()
    games = {}
    for row in rows:
        game_id, player1, player2, winner, player, beer_count = row
        if game_id not in games:
            games[game_id] = {
                "id": game_id,
                "player1": player1,
                "player2": player2,
                "winner": winner,
                "beers": {player1: 0, player2: 0}
            }
        games[game_id]["beers"][player] = beer_count

    conn.close()
    return jsonify(list(games.values()))

if __name__ == '__main__':
    app.run(debug=True)
