import os
import psycopg2
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# ===== ДАННЫЕ ИЗ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ (безопасно!) =====
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

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)