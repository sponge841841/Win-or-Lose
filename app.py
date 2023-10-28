from dotenv import load_dotenv
from flask import Flask, request, render_template, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user
import mysql.connector
import os
from user_model import User

# FlaskとFlask-Loginの初期化
app = Flask(__name__)
app.secret_key = os.environ['SECRET_KEY']
login_manager = LoginManager()
login_manager.init_app(app)
load_dotenv()

# MySQL接続設定
config = {
    'user': os.environ['DB_USERNAME'],
    'password': os.environ['DB_PASSWORD'],
    'host': os.environ['DB_SERVER'],
    'database': os.environ['DB_NAME'],
    'charset': 'utf8'
}

# ユーザーローダーの定義
@LoginManager.user_loader
def load_user(user_id):
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    row = cursor.fetchone()
    cursor.close()
    cnx.close()
    if row:
        return User(row['id'], row['username'], row['email'], row['password_hash'])
    else:
        return None

# ルーティングとビュー関数
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        action = request.form['action']

        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor(dictionary=True)

        if action == 'register':
            # 新規登録処理
            cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)", (username, email, password))
            cnx.commit()
            new_user_id = cursor.lastrowid
            login_user(User(new_user_id, username, email, password))

        elif action == 'login':
            # ログイン処理
            cursor.execute("SELECT * FROM users WHERE username = %s AND email = %s AND password_hash = %s", (username, email, password))
            row = cursor.fetchone()
            if row:
                login_user(User(row['id'], row['username'], row['email'], row['password_hash']))

        cursor.close()
        cnx.close()
        
        return redirect(url_for('protected'))
        
    return render_template('index.html')

@app.route('/protected')
@login_required
def protected():
    return "This is a protected page."

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# アプリの実行
if __name__ == '__main__':
    app.run(debug=True)
