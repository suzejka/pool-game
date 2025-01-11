from flask import Flask, render_template, request, redirect, url_for, session, flash
import psycopg2
import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from flask import session, redirect, url_for
from datetime import datetime, timedelta

load_dotenv()

app = Flask(__name__)

# Konfiguracja przesyłania plików
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'supersecretkey'

DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_NAME = os.getenv("DATABASE_NAME")

def init_db():
    with psycopg2.connect(
        host=DATABASE_HOST,
        database=DATABASE_NAME,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD
    ) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                nickname TEXT NOT NULL,
                avatar TEXT,
                beer_count INTEGER DEFAULT 0
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS games (
                id SERIAL PRIMARY KEY,
                player1 TEXT,
                player2 TEXT,
                winner TEXT,
                game_type TEXT,
                date TIMESTAMP DEFAULT NOW()
            )
        ''')
        conn.commit()

init_db()

# Strona główna
@app.route('/')
def index():
    if 'nickname' in session:
        nickname = session['nickname']
        with psycopg2.connect( 
            host=DATABASE_HOST,
            database=DATABASE_NAME,
            user=DATABASE_USER,
            password=DATABASE_PASSWORD
            ) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE nickname = %s', (nickname,))
            user = cursor.fetchone()
            if user:
                cursor = conn.cursor()
                cursor.execute('SELECT beer_count FROM users WHERE nickname = %s', (nickname,))
                beers = cursor.fetchone()
                cursor.execute('SELECT COUNT(*) FROM games WHERE winner = %s', (nickname,))
                games = cursor.fetchone()

                games_count = games[0] if games else 0
                beers_count = beers[0] if beers else 0

                return render_template('index.html', user=nickname, avatar=user[2], games=games_count, beers=beers_count)  # Avatar z bazy danych
             # Jeśli brak użytkownika w bazie
    return redirect(url_for('login'))  # Jeśli nie ma zalogowanego użytkownika

# Strona logowania
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nickname = request.form['nickname']
        
        # Sprawdzenie, czy użytkownik istnieje w bazie
        with psycopg2.connect( 
            host=DATABASE_HOST,
            database=DATABASE_NAME,
            user=DATABASE_USER,
            password=DATABASE_PASSWORD
            ) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE nickname = %s', (nickname,))
            user = cursor.fetchone()
        
        # Jeśli użytkownik nie istnieje, przekierowanie do strony dodawania avatara
        if user:
            session['nickname'] = nickname
            return redirect(url_for('index'))
        else:
            with psycopg2.connect( 
            host=DATABASE_HOST,
            database=DATABASE_NAME,
            user=DATABASE_USER,
            password=DATABASE_PASSWORD
            ) as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO users (nickname, avatar) VALUES (%s, %s)', 
                               (nickname, "path"))
        
            session['nickname'] = nickname
            return redirect(url_for('index'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()  # Wyczyść sesję użytkownika
    return redirect(url_for('login'))  # Przekieruj na stronę logowania

@app.route('/your_games')
def your_games():
    today = datetime.now().date()
    seven_days_ago = today - timedelta(days=7)
    
    # Odczytaj nickname z sesji
    nickname = session.get('nickname')  # Załóżmy, że nickname jest zapisany w sesji

    # Jeśli brak nickname, użytkownik nie jest zalogowany, przekieruj
    if not nickname:
        return redirect(url_for('login'))  # Możesz przekierować do strony logowania

    with psycopg2.connect(
        host=DATABASE_HOST,
        database=DATABASE_NAME,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD
    ) as conn:
        cursor = conn.cursor()
        
        # Gry z dzisiaj, gdzie nickname pasuje do gracza
        cursor.execute('''
            SELECT player1, player2, winner, game_type, date::date AS game_date
            FROM games 
            WHERE (player1 = %s OR player2 = %s) AND date::date = %s
            ORDER BY date DESC
        ''', (nickname, nickname, today))
        today_games = cursor.fetchall()
        
        # Gry z ostatnich 7 dni, gdzie nickname pasuje do gracza
        cursor.execute('''
            SELECT player1, player2, winner, game_type, date::date AS game_date
            FROM games 
            WHERE (player1 = %s OR player2 = %s) AND date::date BETWEEN %s AND %s
            AND date::date != %s
            ORDER BY date DESC
        ''', (nickname, nickname, seven_days_ago, today, today))
        past_week_games = cursor.fetchall()
    
    return render_template(
        'your_games.html',
        today_games=today_games,
        past_week_games=past_week_games
    )

@app.route('/all_games')
def all_games():
    today = datetime.now().date()
    seven_days_ago = today - timedelta(days=7)
    
    # Odczytaj nickname z sesji
    nickname = session.get('nickname')  # Załóżmy, że nickname jest zapisany w sesji

    # Jeśli brak nickname, użytkownik nie jest zalogowany, przekieruj
    if not nickname:
        return redirect(url_for('login'))  # Możesz przekierować do strony logowania

    with psycopg2.connect(
        host=DATABASE_HOST,
        database=DATABASE_NAME,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD
    ) as conn:
        cursor = conn.cursor()
        
        # Gry z dzisiaj, gdzie nickname pasuje do gracza
        cursor.execute('''
            SELECT player1, player2, winner, game_type, date::date AS game_date
            FROM games 
            WHERE date::date = %s
            ORDER BY date DESC
        ''', (today,))
        today_games = cursor.fetchall()
        
        # Gry z ostatnich 7 dni, gdzie nickname pasuje do gracza
        cursor.execute('''
            SELECT player1, player2, winner, game_type, date::date AS game_date
            FROM games 
            WHERE date::date BETWEEN %s AND %s
            AND date::date != %s
            ORDER BY date DESC
        ''', (seven_days_ago, today, today))
        past_week_games = cursor.fetchall()
    
    return render_template(
        'your_games.html',
        today_games=today_games,
        past_week_games=past_week_games
    )

# # Strona dodawania avatara
# @app.route('/add_avatar', methods=['GET', 'POST'])
# def add_avatar():
#     if request.method == 'POST':
#         avatar = request.files.get('avatar')
        
#         if avatar:
#             # Zapisz avatar w folderze
#             filename = secure_filename(avatar.filename)
#             avatar_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#             avatar.save(avatar_path)
            
#             # Zapisz avatar do bazy danych
#             with psycopg2.connect( 
#                 host=DATABASE_HOST,
#                 database=DATABASE_NAME,
#                 user=DATABASE_USER,
#                 password=DATABASE_PASSWORD
#                 ) as conn:
#                 cursor = conn.cursor()
#                 cursor.execute('INSERT INTO users (nickname, avatar) VALUES (%s, %s)', 
#                                (session['nickname'], avatar_path))
#                 conn.commit()
            
#         return redirect(url_for('index'))
        
#     return render_template('add_avatar.html')

@app.route('/add_game', methods=['GET', 'POST'])
def add_game():
    if 'nickname' not in session:
        return redirect(url_for('login'))  # Jeśli brak nickname, przekierowanie do logowania
    
    if request.method == 'POST':
        player1 = request.form['player1']
        player2 = request.form['player2']

        # Sprawdzamy, który checkbox jest zaznaczony i zapisujemy zwycięzcę
        winner = request.form.get('winner')

        # Jeśli żaden checkbox nie jest zaznaczony, ustawiamy zwycięzcę jako "Remis"
        if not winner:
            winner = "Remis"
        else:
            # Odczytujemy dokładny nickname zwycięzcy (player1 lub player2)
            if winner == 'player1':
                winner = player1
            elif winner == 'player2':
                winner = player2

        # Pobieramy typ gry (8-ball lub 9-ball)
        game_type = request.form.get('game_type')

        # Sprawdzamy, czy typ gry został wybrany
        if not game_type:
            return render_template('add_game.html', error="Wybierz poprawny typ gry (8-ball lub 9-ball).")

        # Zapisz grę do bazy danych
        with psycopg2.connect(
            host=DATABASE_HOST,
            database=DATABASE_NAME,
            user=DATABASE_USER,
            password=DATABASE_PASSWORD
        ) as conn:
            cursor = conn.cursor()
            cursor.execute(''' 
                INSERT INTO games (player1, player2, winner, game_type) 
                VALUES (%s, %s, %s, %s)
            ''', (player1, player2, winner, game_type))
            conn.commit()

        return redirect(url_for('index'))  # Przekierowanie na stronę główną

    # Pobierz listę wszystkich użytkowników (nickname)
    with psycopg2.connect(
        host=DATABASE_HOST,
        database=DATABASE_NAME,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD
    ) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT nickname FROM users")  # Pobieramy tylko nicknames
        users = cursor.fetchall()

    return render_template('add_game.html', users=users)



@app.route('/add_beer', methods=['POST'])
def add_beer():
    if 'nickname' in session:
        nickname = session['nickname']
        with psycopg2.connect( 
            host=DATABASE_HOST,
            database=DATABASE_NAME,
            user=DATABASE_USER,
            password=DATABASE_PASSWORD
            ) as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET beer_count = beer_count + 1 WHERE nickname = %s', (nickname,))
            conn.commit()
        return redirect(url_for('index'))  # Po dodaniu piwa wróć do strony głównej
    return redirect(url_for('login'))

# Uruchomienie aplikacji
if __name__ == '__main__':
    app.run(debug=True)
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
