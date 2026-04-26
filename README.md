# 🎒 Campus Lost & Found System

A smart, secure, and user-friendly web platform designed to help students report, search, and recover lost items within a campus.

---

## 🚀 Features

### 👤 User Features

* 🔐 Login/Register with institutional email (`@mlrit.ac.in`)
* 📦 Add Lost/Found items with details & image
* 🔍 Browse and search items
* 💬 Chat with the person who posted the item
* 📊 View dashboard statistics

### 🛠️ Admin Features

* ✅ Approve / Reject items
* 🔄 Mark items as Found / Pending
* 🗑️ Delete inappropriate items
* 🚨 View reported items
* 📊 Analytics dashboard

### 💡 Advanced Features

* 🤖 Matching Algorithm (Lost ↔ Found items suggestion)
* 💬 Real-time chat (auto-refresh based)
* 🖼️ Image upload support
* 🎨 Modern UI with glassmorphism & gradient design

---

## 🧠 Matching Algorithm

The system intelligently suggests possible matches between lost and found items based on:

* Title similarity
* Description keywords
* Location matching
* Category matching

This helps users quickly identify potential matches.

---

## 🏗️ Tech Stack

* **Frontend:** HTML, CSS (Glassmorphism UI)
* **Backend:** Python (Flask)
* **Database:** SQLite
* **Other:** Jinja2 Templates

---

## 📁 Project Structure

```
Campus-Lost-Found/
│
├── static/
│   ├── style.css
│   └── campus.jpg
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── dashboard.html
│   ├── admin.html
│   ├── chat.html
│   ├── analytics.html
│   └── add.html
│
├── uploads/          # Uploaded images
├── database.db
├── app.py
└── README.md
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository

```
git clone https://github.com/your-username/campus-lost-found.git
cd campus-lost-found
```

### 2️⃣ Install dependencies

```
pip install flask
```

### 3️⃣ Run the app

```
python app.py
```

### 4️⃣ Open in browser

```
http://127.0.0.1:5000
```

---

## 🔑 Default Admin Login

```
Role: Admin
Password: admin123
```

---

## 🎯 Future Enhancements

* 🔔 Email notifications for matches
* 📱 Mobile responsive improvements
* ⚡ True real-time chat (WebSockets)
* 🧠 AI-based image matching
* 🔎 Advanced filters & search

---

## 📸 Screenshots

* Landing Page (Modern UI with blurred campus background)
* Dashboard (Stats + Item cards)
* Chat System
* Admin Panel

---

##  Inspiration

> “Every belonging deserves to return home.”

---

## 👩‍💻 Author

**Ashritha K**

---

## 📄 License

This project is for educational and academic purposes.
# Campus-lost-and-found-portal
Campus lost and found portal
