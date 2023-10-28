from flask_login import LoginManager, UserMixin
from dotenv import load_dotenv

# ユーザーモデルの定義
class User(UserMixin):
    def __init__(self, id, username, email, password_hash):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash



