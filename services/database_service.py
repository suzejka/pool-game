import psycopg2
import os
from models.user import User

# module fot database operations
DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_NAME = os.getenv("DATABASE_NAME")

def connect():
    return psycopg2.connect(
        host=DATABASE_HOST,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
        dbname=DATABASE_NAME
    )

def get_users():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    cur.close()
    conn.close()

    users = [User(user_id, username, password) for user_id, username, password in users]
    return users

def get_user(username):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user

def add_user(username, password):
    conn = connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
    conn.commit()
    cur.close()
    conn.close()

def get_user_by_id(user_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user

def get_user_by_username(username):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user

def get_user_id(username):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE username = %s", (username,))
    user_id = cur.fetchone()[0]
    cur.close()
    conn.close()
    return user_id

def get_games():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM games")
    games = cur.fetchall()
    cur.close()
    conn.close()
    return games

def add_game(player1_id, player2_id, winner_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO games (player1_id, player2_id, winner_id) VALUES (%s, %s, %s)", (player1_id, player2_id, winner_id))
    conn.commit()
    cur.close()
    conn.close()

def get_beers(user_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM beers WHERE user_id = %s", (user_id,))
    beers = cur.fetchall()
    cur.close()
    conn.close()
    return beers

def count_beers(user_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM beers WHERE user_id = %s", (user_id,))
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count

def add_beer(user_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO beers (user_id) VALUES (%s)", (user_id,))
    conn.commit()
    cur.close()
    conn.close()

def get_won_games(user_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM games WHERE winner_id = %s", (user_id,))
    won_games = cur.fetchall()
    cur.close()
    conn.close()
    return won_games

def get_all_games(user_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM games WHERE player1_id = %s OR player2_id = %s", (user_id, user_id))
    all_games = cur.fetchall()
    cur.close()
    conn.close()
    return all_games


