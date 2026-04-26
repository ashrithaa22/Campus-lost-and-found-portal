from flask import Flask, render_template, request, redirect, send_from_directory, session
import sqlite3, os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "secret123"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ================= DATABASE =================
def init_db():
    with sqlite3.connect("database.db") as conn:
        c = conn.cursor()

        # ITEMS
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

        # CHAT
        c.execute("""
        CREATE TABLE IF NOT EXISTS chats(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER,
        sender TEXT,
        message TEXT,
        time TEXT
        )
        """)

        # REPORTS
        c.execute("""
        CREATE TABLE IF NOT EXISTS reports(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER,
        reason TEXT
        )
        """)

init_db()

# ================= HOME =================
@app.route("/")
def home():
    return render_template("index.html")

# ================= REGISTER =================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email").strip().lower()

        if not email.endswith("@mlrit.ac.in"):
            return "❌ Only @mlrit.ac.in emails allowed!"

        return redirect("/login")

    return render_template("register.html")

# ================= LOGIN =================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        role = request.form.get("role")
        email = request.form.get("email").strip().lower()
        password = request.form.get("password")

        # EMAIL CHECK
        if not email.endswith("@mlrit.ac.in"):
            return "❌ Only @mlrit.ac.in emails allowed!"

        # ADMIN
        if role == "admin" and password == "admin123":
            session["user"] = "admin"
            return redirect("/admin")

        # STUDENT
        session["user"] = email
        return redirect("/dashboard")

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
        item_type = request.form.get("type")

        status = "Pending"   # 🔥 IMPORTANT

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

        return redirect("/dashboard")

    return render_template("add.html")
    # ================= AI MATCHING =================
def calculate_match_score(item1, item2):
    score = 0

    # Title match
    if item1[1].lower() in item2[1].lower() or item2[1].lower() in item1[1].lower():
        score += 30

    # Description match
    if item1[2] and item2[2]:
        if item1[2].lower() in item2[2].lower() or item2[2].lower() in item1[2].lower():
            score += 20

    # Color match
    if item1[3] and item2[3] and item1[3].lower() == item2[3].lower():
        score += 15

    # Location match
    if item1[4] and item2[4] and item1[4].lower() == item2[4].lower():
        score += 20

    # Category match
    if item1[8] and item2[8] and item1[8].lower() == item2[8].lower():
        score += 15

    return score


def find_matches(items):
    matches = []

    for i in items:
        for j in items:

            # Only match LOST with FOUND
            if i[10] == "lost" and j[10] == "found":

                score = calculate_match_score(i, j)

                if score >= 40:  # threshold
                    matches.append({
                        "lost": i,
                        "found": j,
                        "score": score
                    })

    # sort by best match
    matches = sorted(matches, key=lambda x: x["score"], reverse=True)

    return matches[:5]  # top 5 matches

# ================= DASHBOARD =================
@app.route("/dashboard")
def dashboard():
    user = session.get("user")

    with sqlite3.connect("database.db") as conn:
        c = conn.cursor()

        # GET ITEMS
        c.execute("SELECT * FROM items WHERE status='Approved' ORDER BY id DESC")
        items = c.fetchall()

        # 🔥 FIND MATCHES
        matches = find_matches(items)

        # 🔥 CREATE MATCHED ITEM IDS
        matched_ids = set()
        for m in matches:
            matched_ids.add(m["lost"][0])
            matched_ids.add(m["found"][0])

        # STATS
        c.execute("SELECT COUNT(*) FROM items")
        total = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM items WHERE type='lost'")
        lost = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM items WHERE type='found'")
        found = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM items WHERE status='Pending'")
        pending = c.fetchone()[0]

    return render_template("dashboard.html",
                           items=items,
                           matches=matches,
                           matched_ids=matched_ids,   # 🔥 NEW
                           total=total,
                           lost=lost,
                           found=found,
                           pending=pending,
                           user=user)

# ================= ADMIN =================
@app.route("/admin")
def admin():
    if session.get("user") != "admin":
        return redirect("/login")

    with sqlite3.connect("database.db") as conn:
        c = conn.cursor()

        c.execute("SELECT * FROM items ORDER BY id DESC")
        items = c.fetchall()

        # REPORTS
        c.execute("""
        SELECT reports.id, items.title, reports.reason
        FROM reports
        JOIN items ON reports.item_id = items.id
        """)
        reports = c.fetchall()

    return render_template("admin.html", items=items, reports=reports)

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

# ================= STATUS =================
@app.route("/status/<int:id>/<new_status>")
def status(id, new_status):
    with sqlite3.connect("database.db") as conn:
        c = conn.cursor()
        c.execute("UPDATE items SET status=? WHERE id=?", (new_status, id))
        conn.commit()

    return redirect("/admin")

# ================= DELETE =================
@app.route("/delete/<int:id>")
def delete(id):
    with sqlite3.connect("database.db") as conn:
        c = conn.cursor()
        c.execute("DELETE FROM items WHERE id=?", (id,))
        conn.commit()

    return redirect("/admin")

# ================= CHAT =================
@app.route("/chat/<int:item_id>", methods=["GET", "POST"])
def chat(item_id):
    user = session.get("user")

    # convert email → name
    username = user.split("@")[0]

    with sqlite3.connect("database.db") as conn:
        c = conn.cursor()

        # SEND MESSAGE
        if request.method == "POST":
            msg = request.form.get("msg")

            if msg:
                time = datetime.now().strftime("%H:%M")

                c.execute("""
                INSERT INTO chats(item_id,sender,message,time)
                VALUES(?,?,?,?)
                """, (item_id, username, msg, time))
                conn.commit()

            return redirect(f"/chat/{item_id}")

        # GET CHAT
        c.execute("""
        SELECT sender, message, time
        FROM chats
        WHERE item_id=?
        ORDER BY id
        """, (item_id,))
        chats = c.fetchall()

    return render_template("chat.html", chats=chats, user=username)

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

    return render_template("analytics.html",
                           total=total,
                           approved=approved,
                           pending=pending,
                           found=found)

# ================= IMAGE =================
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)