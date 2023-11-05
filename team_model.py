from flask_login import UserMixin

# チームモデルの定義
class Team(UserMixin):
    def __init__(self, id, team_name, password_hash):
        self.id = id
        self.team_name = team_name
        self.password_hash = password_hash
