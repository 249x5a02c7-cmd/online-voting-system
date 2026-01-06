from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = "secure_voting_key"

def get_db():
    return sqlite3.connect("voting.db")

# ---------- CREATE TABLES ----------
with get_db() as con:
    con.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            voter_id TEXT UNIQUE,
            password TEXT
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            voter_id TEXT UNIQUE,
            candidate TEXT
        )
    """)

# ---------- REGISTER ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        voter_id = request.form.get("voter_id")
        password = request.form.get("password")

        try:
            with get_db() as con:
                con.execute(
                    "INSERT INTO users (voter_id, password) VALUES (?, ?)",
                    (voter_id, password)
                )
            return redirect("/login")
        except sqlite3.IntegrityError:
            return render_template(
                "register.html",
                error="Voter ID already exists. Please login."
            )

    return render_template("register.html")

# ---------- LOGIN ----------
# ---------- ADMIN LOGIN ----------
@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        admin_id = request.form.get("admin_id")
        password = request.form.get("password")

        if admin_id == "admin" and password == "admin123":
            session["admin"] = True
            return redirect("/admin_results")
        else:
            return render_template(
                "admin_login.html",
                error="Invalid Admin Credentials"
            )

    return render_template("admin_login.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        voter_id = request.form.get("voter_id")
        password = request.form.get("password")

        with get_db() as con:
            cur = con.cursor()
            cur.execute(
                "SELECT * FROM users WHERE voter_id=? AND password=?",
                (voter_id, password)
            )
            user = cur.fetchone()

        if user:
            session["voter_id"] = voter_id
            return redirect("/")
        else:
            return render_template(
                "login.html",
                error="Invalid Voter ID or Password"
            )

    return render_template("login.html")

# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---------- VOTING PAGE ----------
@app.route("/")
def index():
    if "voter_id" not in session:
        return redirect("/login")
    return render_template("index.html", voter_id=session["voter_id"])

# ---------- SUBMIT VOTE ----------
@app.route("/vote", methods=["POST"])
def vote():
    if "voter_id" not in session:
        return jsonify({"status": "not_logged_in"})

    voter_id = session["voter_id"]
    candidate = request.json["candidate"]

    try:
        with get_db() as con:
            con.execute(
                "INSERT INTO votes (voter_id, candidate) VALUES (?, ?)",
                (voter_id, candidate)
            )
        return jsonify({"status": "success"})
    except sqlite3.IntegrityError:
        return jsonify({"status": "already_voted"})

# ---------- RESULTS PAGE ----------
# ---------- ADMIN RESULTS PAGE ----------
@app.route("/admin_results")
def admin_results():
    if "admin" not in session:
        return redirect("/admin")

    with get_db() as con:
        cur = con.cursor()
        cur.execute("""
            SELECT candidate, COUNT(*)
            FROM votes
            GROUP BY candidate
        """)
        rows = cur.fetchall()

    result = {
        "tdp": 0,
        "ycp": 0,
        "bjp": 0,
        "brs": 0,
        "congress": 0,
        "janasena": 0,
        "nota": 0
    }

    for candidate, count in rows:
        if candidate in result:
            result[candidate] = count

    return render_template("results.html", result=result)
@app.route("/admin_logout")
def admin_logout():
    session.pop("admin", None)
    return redirect("/admin")


import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

