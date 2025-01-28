from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2
from services import database_service as db

app = Flask(__name__)
app.secret_key = '3a26ac0d-7470-43fd-98a3-1bb7de9bad33'

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not db.get_user(username) or db.get_user(username).password != password:
            return render_template('index.html', error="Nieprawidłowy login lub hasło")
        session['username'] = username
        return render_template('home.html', username=username)
    return render_template('index.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    return render_template('home.html', username=username)
    

# Dodawanie gry
@app.route('/add-game', methods=['GET', 'POST'])
def add_game():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        print(request.form)
        opponent = request.form['opponent']
        winner = request.form['winner']
        game_type = request.form['game_type']

        winner = session['username'] if winner == "Ty" else opponent
        print(f"Winner: {winner}")

        db.add_game(
            db.get_user_id(session['username']), 
            db.get_user_id(opponent),
            db.get_user_id(winner),
            game_type
            )
        return redirect(url_for('home'))

    return render_template('add-game.html', users=db.get_user_without_current_user_by_username(session['username']))

# Dodawanie piwa
@app.route('/add-beer', methods=['GET', 'POST'])
def add_beer():
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    if request.method == 'POST':
        db.add_beer(db.get_user(username).id)
        return redirect(url_for('home'))

# Statystyki
@app.route('/stats')
def stats(): # Debug print
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    won_games = db.count_won_games(db.get_user(username).id)
    all_games = db.count_all_games(db.get_user(username).id)
    beers = db.count_beers(db.get_user(username).id)
    return render_template('stats.html', won_games=won_games, all_games=all_games, beers=beers)

@app.route('/friends')
def friends(): # Debug print
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    return render_template('friends.html')

# sign up
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db.add_user(username, password)        
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/sign-out')
def signout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
