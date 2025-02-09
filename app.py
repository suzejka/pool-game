from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2
from services import database_service as db
from services import email_service as es
import traceback
from models.models import Idea

app = Flask(__name__)
app.secret_key = '3a26ac0d-7470-43fd-98a3-1bb7de9bad33'

@app.route('/', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            if not db.get_user(username) or db.get_user(username).password != password:
                return render_template('index.html', error="Nieprawidłowy login lub hasło")
            session['username'] = username
            return render_template('home.html', username=username)
        return render_template('index.html')
    except Exception as e:
        es.send_error_email(str(e), traceback.format_exc())
        return render_template('error_page.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    try:
        if 'username' not in session:
            return redirect(url_for('login'))
        username = session['username']
        return render_template('home.html', username=username)
    except Exception as e:
        es.send_error_email(str(e), traceback.format_exc(), session['username'])
        return render_template('error_page.html')

@app.route('/add-game', methods=['GET', 'POST'])
def add_game():
    try:
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
    except Exception as e:
        es.send_error_email(str(e), traceback.format_exc(), session['username'])
        return render_template('error_page.html')

@app.route('/add-beer', methods=['GET', 'POST'])
def add_beer():
    try:
        if 'username' not in session:
            return redirect(url_for('login'))
        username = session['username']
        if request.method == 'POST':
            db.add_beer(db.get_user(username).id)
            return redirect(url_for('home'))
    except Exception as e:
        es.send_error_email(str(e), traceback.format_exc(), session['username'])
        return render_template('error_page.html')

@app.route('/stats')
def stats():
    try:
        if 'username' not in session:
            return redirect(url_for('login'))
        username = session['username']
        won_games = db.count_won_games(db.get_user(username).id)
        all_games = db.count_all_games(db.get_user(username).id)
        beers = db.count_beers(db.get_user(username).id)
        return render_template('stats.html', won_games=won_games, all_games=all_games, beers=beers)
    except Exception as e:
        es.send_error_email(str(e), traceback.format_exc(), session['username'])
        return render_template('error_page.html')

@app.route('/friends')
def friends():
    try:
        if 'username' not in session:
            return redirect(url_for('login'))
        username = session['username']
        return render_template('friends.html')
    except Exception as e:
        es.send_error_email(str(e), traceback.format_exc(), session['username'])
        return render_template('error_page.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    try:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            db.add_user(username, password)        
            return redirect(url_for('login'))
        return render_template('signup.html')
    except Exception as e:
        es.send_error_email(str(e), traceback.format_exc(), session['username'])
        return render_template('error_page.html')
    
@app.route('/account-settings', methods=['GET', 'POST'])
def account_settings():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        # Handle account settings changes here
        pass
    return render_template('account.html')

@app.route('/change-username', methods=['POST'])
def change_username():
    if 'username' not in session:
        return redirect(url_for('login'))
    new_username = request.form['new-username']
    user = db.get_user(session['username'])
    db.update_username(user.id, new_username)
    session['username'] = new_username
    return redirect(url_for('home'))

@app.route('/change-password', methods=['POST'])
def change_password():
    if 'username' not in session:
        return redirect(url_for('login'))
    new_password = request.form['new-password']
    user = db.get_user(session['username'])
    db.update_password(user.id, new_password)
    return redirect(url_for('home'))

@app.route('/ideas', methods=['GET', 'POST'])
def ideas():
    try:
        if 'username' not in session:
            return redirect(url_for('login'))
        if request.method == 'POST':
            message_type = request.form['message-type']
            description = request.form['description']

            idea = Idea(
                idea_id=None,
                type=message_type,
                description=description,
                user_id=db.get_user_id(session['username'])
            )

            db.create_idea(idea)
            es.send_idea_email(idea)
            return redirect(url_for('home'))
        return render_template('ideas.html')
    except Exception as e:
        es.send_error_email(str(e), traceback.format_exc(), session['username'])
        return render_template('error_page.html')


@app.route('/sign-out')
def signout():
    try:
        session.pop('username', None)
        return redirect(url_for('login'))
    except Exception as e:
        es.send_error_email(str(e), traceback.format_exc())
        return render_template('error_page.html')

if __name__ == '__main__':
    app.run(debug=True)
