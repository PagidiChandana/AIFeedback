from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from textblob import TextBlob

app = Flask(__name__)
CORS(app)

# ---------------- DATABASE CONNECTION ----------------
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


# ---------------- CREATE TABLES ----------------



# ---------------- REGISTER ----------------
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
            (data["name"], data["email"], data["password"], data["role"])
        )
        conn.commit()
        return jsonify({"message": "User Registered Successfully"})
    
    except sqlite3.IntegrityError:
        return jsonify({"message": "Email already exists"})
    
    except Exception as e:
        return jsonify({"message": str(e)})  # shows real error
    
    finally:
        conn.close()


# ---------------- LOGIN ----------------
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (data["email"], data["password"])
    )
    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({
            "status": "success",
            "user": dict(user)
        })
    else:
        return jsonify({"status": "fail"})


# ---------------- GIVE FEEDBACK ----------------
@app.route("/give-feedback", methods=["POST"])
def give_feedback():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()

    analysis = TextBlob(data["message"])
    sentiment = "Positive" if analysis.sentiment.polarity > 0 else "Negative"

    cursor.execute(
        "INSERT INTO feedback (from_user, to_user, message, sentiment) VALUES (?, ?, ?, ?)",
        (data["from_user"], data["to_user"], data["message"], sentiment)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Feedback Submitted",
        "sentiment": sentiment
    })


# ---------------- GET USERS BY ROLE ----------------
@app.route("/users/<role>", methods=["GET"])
def get_users(role):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, name FROM users WHERE role=?",
        (role,)
    )
    users = cursor.fetchall()
    conn.close()

    return jsonify([dict(user) for user in users])

def create_tables():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_user INTEGER,
        to_user INTEGER,
        message TEXT,
        sentiment TEXT
    )
    """)

    conn.commit()
    conn.close()

def insert_default_users():
    conn = get_db()
    cursor = conn.cursor()

    users = [
        # Students
        ("chandana", "chandana@gmail.com", "123", "student"),
        ("nikhitha", "nikhitha@gmail.com", "123", "student"),
        ("deekshitha", "deekshitha@gmail.com", "123", "student"),
        ("priya", "priya@gmail.com", "123", "student"),
        ("gowri", "gowri@gmail.com", "123", "student"),

        # Faculty
        ("madar", "madar@gmail.com", "123", "faculty"),
        ("siva prasad", "sivaprasad@gmail.com", "123", "faculty"),
        ("rashmi", "rashmi@gmail.com", "123", "faculty"),
        ("nagesh", "nagesh@gmail.com", "123", "faculty"),
        ("yugandhar", "yugandhar@gmail.com", "123", "faculty"),
    ]

    for user in users:
        try:
            cursor.execute(
                "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                user
            )
        except sqlite3.IntegrityError:
            pass  # ignore if already exists

    conn.commit()
    conn.close()
if __name__ == "__main__":
    create_tables()
    insert_default_users()
    app.run(debug=True)
