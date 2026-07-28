import os
import psycopg2
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# ===== ДАННЫЕ ИЗ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ =====
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")

def get_db():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        sslmode="require"
    )

def get_assets(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT symbol, balance, address, price, name, icon FROM assets WHERE user_id=%s", (user_id,))
    rows = cur.fetchall()
    conn.close()
    return [{"symbol": r[0], "balance": r[1], "address": r[2], "price": r[3], "name": r[4], "icon": r[5]} for r in rows]

def get_user_by_username(username):
    """Ищет пользователя по username (без @) в базе данных"""
    username = username.replace('@', '').strip().lower()
    conn = get_db()
    cur = conn.cursor()
    # В базе у нас нет прямого поля username, но мы можем искать по адресам или другим полям
    # Пока ищем по всем активам и возвращаем первый найденный user_id
    cur.execute("SELECT DISTINCT user_id FROM assets")
    users = cur.fetchall()
    conn.close()
    
    # Для демо-режима: пробуем найти пользователя по username в адресах
    # Это упрощённый вариант, в реальности нужно хранить username в отдельной таблице
    for user in users:
        user_id = user[0]
        assets = get_assets(user_id)
        for a in assets:
            if username in a['address'].lower():
                return user_id
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/balance/<int:user_id>')
def get_balance(user_id):
    assets = get_assets(user_id)
    total_usd = sum(a["balance"] * a["price"] for a in assets)
    return jsonify({
        "total_usd": total_usd,
        "assets": assets
    })

@app.route('/api/get_user_id/<username>')
def get_user_id(username):
    """Возвращает user_id по username"""
    user_id = get_user_by_username(username)
    if user_id:
        return jsonify({"user_id": user_id})
    else:
        return jsonify({"error": "User not found"}), 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
