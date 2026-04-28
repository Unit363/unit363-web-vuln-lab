from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "labsecret"

def get_db():
    db = sqlite3.connect("blog.db")
    db.row_factory = sqlite3.Row 
    return db

def init_db():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            title   TEXT NOT NULL,
            content TEXT
        )
    """)
    # Seed a default post if table is empty
    count = db.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
    if count == 0:
        db.execute("INSERT INTO posts (title, content) VALUES (?, ?)",
                   ["Welcome!", "This is the default post."])
        
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role     TEXT NOT NULL DEFAULT 'reader'
        )
    """)
    # Seed default users
    if db.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        db.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                   ["admin", "admin123", "admin"])
        db.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                   ["user", "user123", "reader"])
    db.commit()

@app.route("/")
def index():
    db = get_db()
    posts = db.execute("SELECT * FROM posts ORDER BY id DESC").fetchall()
    return render_template("index.html", posts=posts)

@app.route("/post", methods=["POST"])
def create_post():
    db = get_db()
    db.execute("INSERT INTO posts (title, content) VALUES (?, ?)",
               [request.form["title"], request.form["content"]])
    db.commit()
    return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username = ?", [username]
        ).fetchone()

        if user and user["password"] == password:
            session["user"] = user["username"]
            session["role"] = user["role"]
            return redirect("/")
        error = "Wrong username or password"
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)