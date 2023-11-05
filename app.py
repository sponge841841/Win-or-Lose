from dotenv import load_dotenv
from flask import Flask, request, render_template, redirect, url_for, session
from flask_login import LoginManager, login_required, logout_user
import mysql.connector
import os
from werkzeug.security import generate_password_hash, check_password_hash

from team_model import Team

# FlaskとFlask-Loginの初期化
load_dotenv()
app = Flask(__name__)
app.secret_key = os.environ['SECRET_KEY']
login_manager = LoginManager()
login_manager.init_app(app)

# MySQL接続設定
config = {
    'user': os.environ['DB_USERNAME'],
    'password': os.environ['DB_PASSWORD'],
    'host': os.environ['DB_SERVER'],
    'database': os.environ['DB_NAME'],
    'charset': 'utf8'
}

# ユーザーローダーの定義（チームに変更）
@login_manager.user_loader
def load_user(team_id):
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor(dictionary=True)
    cursor.execute("SELECT * FROM teams WHERE id = %s", (team_id,))
    row = cursor.fetchone()
    cursor.close()
    cnx.close()
    if row:
        # UserクラスはTeamクラスに変更する必要があります。
        return Team(row['id'], row['team_name'], row['password_hash'])
    else:
        return None

# ルーティングとビュー関数
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        team_name = request.form['team_name']
        password = request.form['password']
        action = request.form['action']

        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor(dictionary=True)

        if action == 'register':
            # チーム登録処理
            password_hash = generate_password_hash(password)
            cursor.execute("INSERT INTO teams (team_name, password_hash, description) VALUES (%s, %s, %s)", 
                           (team_name, password_hash, 'チームの説明'))
            cnx.commit()
            # ここでチームのセッションを作成します
            session['team_id'] = cursor.lastrowid

        elif action == 'login':
            # チームログイン処理
            cursor.execute("SELECT * FROM teams WHERE team_name = %s", (team_name,))
            row = cursor.fetchone()
            if row and check_password_hash(row['password_hash'], password):
                session['team_id'] = row['id']

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
