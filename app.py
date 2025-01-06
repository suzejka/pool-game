from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Konfiguracja przesyłania plików
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'supersecretkey'

# Tworzenie bazy danych
DATABASE = 'database.db'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            nickname TEXT NOT NULL,
                            avatar TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS games (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            player1 TEXT,
                            player2 TEXT,
                            winner TEXT)''')
        conn.commit()

init_db()

# Strona główna
@app.route('/')
def index():
    if 'nickname' in session:
        nickname = session['nickname']
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE nickname = ?', (nickname,))
            user = cursor.fetchone()
            if user:
                cursor = conn.cursor()
                cursor.execute('SELECT beer_count FROM users WHERE nickname = ?', (nickname,))
                beers = cursor.fetchone()
                cursor.execute('SELECT COUNT(*) FROM games WHERE winner = ?', (nickname,))
                games = cursor.fetchone()

                games_count = games[0] if games else 0
                beers_count = beers[0] if beers else 0

                return render_template('index.html', user=nickname, avatar=user[2], games=games_count, beers=beers_count)  # Avatar z bazy danych
            else:
                return redirect(url_for('add_avatar'))  # Jeśli brak użytkownika w bazie
    return redirect(url_for('login'))  # Jeśli nie ma zalogowanego użytkownika

# Strona logowania
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nickname = request.form['nickname']
        
        # Sprawdzenie, czy użytkownik istnieje w bazie
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE nickname = ?', (nickname,))
            user = cursor.fetchone()
        
        # Jeśli użytkownik nie istnieje, przekierowanie do strony dodawania avatara
        if user:
            session['nickname'] = nickname
            return redirect(url_for('index'))
        else:
            session['nickname'] = nickname
            return redirect(url_for('add_avatar'))
    
    return render_template('login.html')

# Strona dodawania avatara
@app.route('/add_avatar', methods=['GET', 'POST'])
def add_avatar():
    if request.method == 'POST':
        avatar = request.files.get('avatar')
        
        if avatar:
            # Zapisz avatar w folderze
            filename = secure_filename(avatar.filename)
            avatar_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            avatar.save(avatar_path)
            
            # Zapisz avatar do bazy danych
            with sqlite3.connect(DATABASE) as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO users (nickname, avatar) VALUES (?, ?)', 
                               (session['nickname'], avatar_path))
                conn.commit()
            
            return redirect(url_for('index'))
        else:
            flash("Proszę wybrać avatar!", "error")
    
    return render_template('add_avatar.html')

# Strona dodawania gry
@app.route('/add_game', methods=['GET', 'POST'])
def add_game():
    if request.method == 'POST':
        player1 = request.form['player1']
        player2 = request.form['player2']

        # Sprawdzamy, który checkbox jest zaznaczony i zapisujemy zwycięzcę
        winner = request.form.get('winner')

        # Jeśli żaden checkbox nie jest zaznaczony, to ustawiamy winner jako 'brak'
        if not winner:
            winner = "Remis"
        else:
            # Odczytujemy dokładny nickname zwycięzcy (player1 lub player2)
            if winner == 'player1':
                winner = player1
            elif winner == 'player2':
                winner = player2

        # Zapisz grę do bazy danych
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO games (player1, player2, winner) 
                              VALUES (?, ?, ?)''', (player1, player2, winner))
            conn.commit()

        return redirect(url_for('index'))  # Przekierowanie na stronę główną lub inną stronę po dodaniu gry

    return render_template('add_game.html')

@app.route('/add_beer', methods=['POST'])
def add_beer():
    if 'nickname' in session:
        nickname = session['nickname']
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET beer_count = beer_count + 1 WHERE nickname = ?', (nickname,))
            conn.commit()
        return redirect(url_for('index'))  # Po dodaniu piwa wróć do strony głównej
    return redirect(url_for('login'))

# Uruchomienie aplikacji
if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
