# -*- coding: utf-8 -*-

from flask import Flask, render_template

# Flaskアプリの初期化
app = Flask(__name__)

# ルートURLの処理
@app.route('/')
def index():
    return render_template('index.html')

# アプリの起動
if __name__ == '__main__':
    app.run(debug=True)
