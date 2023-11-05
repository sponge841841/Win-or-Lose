from dotenv import load_dotenv
from flask import Flask, request, render_template, redirect, url_for, session
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
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
            team = Team(cursor.lastrowid, team_name, password_hash)
            login_user(team) # チームをログインさせる

        elif action == 'login':
            # チームログイン処理
            cursor.execute("SELECT * FROM teams WHERE team_name = %s", (team_name,))
            row = cursor.fetchone()
            if row and check_password_hash(row['password_hash'], password):
                team = Team(row['id'], team_name, row['password_hash'])
                login_user(team) # チームをログインさせる

        cursor.close()
        cnx.close()
        
        return redirect(url_for('home'))
        
    return render_template('index.html')

@app.route('/home')
@login_required
def home():
    # ログインしているチームのIDを取得
    team_id = current_user.get_id()
    
    # データベースに接続
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor(dictionary=True)
    
    # team_dates と scores から情報を取得
    cursor.execute("""
        SELECT td.date, td.comment, s.player_name, s.score
        FROM team_dates AS td
        JOIN scores AS s ON td.id = s.team_date_id
        WHERE td.team_id = %s
        ORDER BY td.date DESC, s.score DESC
    """, (team_id,))
    
    # 結果を整形
    dates_info = {}
    for row in cursor.fetchall():
        date = row['date'].strftime('%Y-%m-%d')
        if date not in dates_info:
            dates_info[date] = {
                'comment': row['comment'],
                'members': []
            }
        dates_info[date]['members'].append({
            'name': row['player_name'],
            'score': row['score']
        })
    
    # データベース接続を閉じる
    cursor.close()
    cnx.close()
    
    # チーム名を取得
    team_name = current_user.team_name
    
    # テンプレートにデータを渡す
    return render_template('home.html', team_name=team_name, dates_info=dates_info)

@app.route('/createscore', methods=['GET', 'POST'])
@login_required
def createscore():
    if request.method == 'POST':
        date = request.form['date']
        comment = request.form['comment']
        team_id = current_user.get_id()  # 現在のユーザー（チーム）IDを取得

        # データベースに接続
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        # team_dates テーブルに新しいエントリを作成
        cursor.execute("INSERT INTO team_dates (team_id, date, comment) VALUES (%s, %s, %s)", 
                       (team_id, date, comment))
        team_date_id = cursor.lastrowid  # 新しく作成されたエントリのIDを取得

        # プレイヤー名とスコアのリストを取得
        player_names = request.form.getlist('player_name[]')
        scores = request.form.getlist('score[]')

        # 各プレイヤーとスコアをデータベースに保存
        for player_name, score in zip(player_names, scores):
            cursor.execute("INSERT INTO scores (team_date_id, player_name, score) VALUES (%s, %s, %s)",
                           (team_date_id, player_name, score))

        # コミットしてデータベース接続を閉じる
        cnx.commit()
        cursor.close()
        cnx.close()

        return redirect(url_for('home'))
    else:
        # GETリクエストの場合はフォームページを表示
        return render_template('createscore.html')
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# アプリの実行
if __name__ == '__main__':
    app.run(debug=True)
