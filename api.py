from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

def check_user(user_id):
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()

    cursor.execute("SELECT has_access FROM users WHERE user_id=?", (user_id,))
    res = cursor.fetchone()

    conn.close()

    if res and res[0] == 1:
        return True
    return False

@app.route("/check")
def check():
    user_id = request.args.get("id")

    if not user_id:
        return jsonify({"access": False})

    if check_user(int(user_id)):
        return jsonify({"access": True})

    return jsonify({"access": False})

app.run(host="0.0.0.0", port=5000)