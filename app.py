from flask import Flask, request, render_template, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv()

# FlaskとFlask拡張の初期化
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://' + os.environ['DB_USERNAME'] + ':' + os.environ['DB_PASSWORD'] + '@' + os.environ['DB_SERVER'] + '/' + os.environ['DB_NAME'] + '?charset=utf8' # MySqlの設定
app.secret_key = os.environ['SECRET_KEY']  # Flask-Loginに必要な秘密鍵
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

# ユーザーモデルの定義
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

# ユーザーローダーの定義
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ルーティングとビュー関数
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        action = request.form['action']

        if action == 'register':
            # 新規登録処理
            new_user = User(username=username, email=email, password_hash=password)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
        elif action == 'login':
            # ログイン処理
            user = User.query.filter_by(username=username, email=email, password_hash=password).first()
            if user:
                login_user(user)
        
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

# データベースの初期化とアプリの実行
if __name__ == '__main__':
    app.run(debug=True)
