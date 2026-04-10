from flask import Flask, render_template, request, redirect, send_from_directory, session
import sqlite3, os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "secret123"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ================= DATABASE INIT =================
def init_db():
    with sqlite3.connect("database.db") as conn:
        c = conn.cursor()

        c.execute("""
        CREATE TABLE IF NOT EXISTS items(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        color TEXT,
        location TEXT,
        date TEXT,
        contact TEXT,
        email TEXT,
        category TEXT,
        image TEXT,
        type TEXT,
        status TEXT
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS chats(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER,
        sender TEXT,
        message TEXT,
        time TEXT
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        password TEXT,
        role TEXT
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS reports(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER,
        reason TEXT
        )
        """)

init_db()

# ================= MATCHING FUNCTION =================
def find_matches(new_item):
    with sqlite3.connect("database.db") as conn:
        c = conn.cursor()

        opposite = "found" if new_item[10] == "lost" else "lost"
        c.execute("SELECT * FROM items WHERE type=?", (opposite,))
        all_items = c.fetchall()

    matches = []

    for item in all_items:
        score = 0

        if new_item[1] and item[1] and new_item[1].lower() in item[1].lower():
            score += 2

        if new_item[3] == item[3]:
            score += 1

        if new_item[4] == item[4]:
            score += 1

        if score >= 2:
            matches.append(item)

    return matches

# ================= HOME =================
@app.route("/")
def home():
    return redirect("/login")

# ================= REGISTER =================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email.endswith("@mlrit.ac.in"):
            return "Use college email only!"

        with sqlite3.connect("database.db") as conn:
            c = conn.cursor()
            c.execute("INSERT INTO users(email,password,role) VALUES(?,?,?)",
                      (email, password, "student"))
            conn.commit()

        return redirect("/login")

    return render_template("register.html")

# ================= LOGIN =================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        role = request.form.get("role")
        email = request.form.get("email")
        password = request.form.get("password")

        if role == "admin" and password == "admin123":
            session["admin"] = True
            return redirect("/admin")

        with sqlite3.connect("database.db") as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
            user = c.fetchone()

        if user:
            session["admin"] = False
            return redirect("/add")

        return "Invalid login"

    return render_template("login.html")

# ================= ADD ITEM =================
@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":

        title = request.form.get("title")
        description = request.form.get("description")
        color = request.form.get("color")
        location = request.form.get("location")
        date = request.form.get("date")
        contact = request.form.get("contact")
        email = request.form.get("email")
        category = request.form.get("category")
        item_type = request.form.get("type", "lost")
        status = "Pending"

        file = request.files.get("image")
        filename = ""

        if file and file.filename != "":
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))

        with sqlite3.connect("database.db") as conn:
            c = conn.cursor()

            c.execute("""
            INSERT INTO items(title,description,color,location,date,contact,email,category,image,type,status)
            VALUES(?,?,?,?,?,?,?,?,?,?,?)
            """, (title, description, color, location, date, contact, email, category, filename, item_type, status))
            conn.commit()

            c.execute("SELECT * FROM items ORDER BY id DESC LIMIT 1")
            new_item = c.fetchone()

        matches = find_matches(new_item)

        return render_template("matches.html", matches=matches)

    return render_template("add.html")

# ================= DASHBOARD =================
@app.route("/dashboard")
def dashboard():
    with sqlite3.connect("database.db") as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM items")
        items = c.fetchall()

    return render_template("dashboard.html", items=items)

# ================= ADMIN =================
@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect("/login")

    with sqlite3.connect("database.db") as conn:
        c = conn.cursor()

        # ITEMS
        c.execute("SELECT * FROM items ORDER BY id DESC")
        items = c.fetchall()

        # 🔥 REPORTS JOIN
        c.execute("""
        SELECT reports.id, items.title, reports.reason
        FROM reports
        JOIN items ON reports.item_id = items.id
        """)
        reports = c.fetchall()

    return render_template("admin.html", items=items, reports=reports)

# ================= STATUS =================
@app.route("/status/<int:id>/<new_status>")
def status(id, new_status):
    if not session.get("admin"):
        return redirect("/login")

    with sqlite3.connect("database.db") as conn:
        c = conn.cursor()
        c.execute("UPDATE items SET status=? WHERE id=?", (new_status, id))
        conn.commit()

    return redirect("/admin")

# ================= DELETE =================
@app.route("/delete/<int:id>")
def delete(id):
    if not session.get("admin"):
        return redirect("/login")

    with sqlite3.connect("database.db") as conn:
        c = conn.cursor()
        c.execute("DELETE FROM items WHERE id=?", (id,))
        conn.commit()

    return redirect("/admin")

# ================= REPORT =================
@app.route("/report/<int:item_id>", methods=["POST"])
def report(item_id):
    reason = request.form.get("reason")

    with sqlite3.connect("database.db") as conn:
        c = conn.cursor()
        c.execute("INSERT INTO reports(item_id,reason) VALUES(?,?)",
                  (item_id, reason))
        conn.commit()

    return redirect("/dashboard")

# ================= ANALYTICS =================
@app.route("/analytics")
def analytics():
    with sqlite3.connect("database.db") as conn:
        c = conn.cursor()

        c.execute("SELECT COUNT(*) FROM items")
        total = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM items WHERE status='Approved'")
        approved = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM items WHERE status='Pending'")
        pending = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM items WHERE status='Found'")
        found = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM reports")
        reports = c.fetchone()[0]

    return render_template("analytics.html",
                           total=total,
                           approved=approved,
                           pending=pending,
                           found=found,
                           reports=reports)

# ================= CHAT =================
@app.route("/chat/<int:item_id>/<user>", methods=["GET", "POST"])
def chat(item_id, user):
    with sqlite3.connect("database.db") as conn:
        c = conn.cursor()

        if request.method == "POST":
            msg = request.form.get("msg")

            if msg:
                time = datetime.now().strftime("%H:%M")

                c.execute(
                    "INSERT INTO chats(item_id,sender,message,time) VALUES(?,?,?,?)",
                    (item_id, user, msg, time)
                )
                conn.commit()

            return redirect(f"/chat/{item_id}/{user}")

        c.execute(
            "SELECT sender, message, time FROM chats WHERE item_id=? ORDER BY id",
            (item_id,)
        )
        chats = c.fetchall()

    return render_template("chat.html", chats=chats, item_id=item_id, user=user)

# ================= IMAGE =================
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)