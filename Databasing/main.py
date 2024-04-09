from flask import Flask, render_template, request, redirect, url_for, session
import pymysql
import os
import datetime
os.environ["SECRET_KEY"] = "password"
app = Flask(__name__, template_folder='templates')
app.secret_key = os.environ["SECRET_KEY"]

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='password',
    database='main'
)

@app.route("/")
def index():
    if "username" in session:
        return redirect(url_for("data"))
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
    user = cursor.fetchone()
    if user:
        session["username"] = username
        return redirect(url_for("data"))
    else:
        return render_template("login.html", error="Invalid username or password")

@app.route("/logout")
def logout():
    session.pop("username", None)
    return render_template("login.html")

@app.route("/data")
def data():
    if "username" not in session:
        return redirect(url_for("index"))
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM data")
    data = cursor.fetchall()

    # Check time 
    queries_today = 0
    today = datetime.datetime.now()
    today = today.strftime("%x")
     
    queries_monthly = 0
    t_month = datetime.datetime.now()
    t_month = t_month.strftime("%m")

    for row in data:
        # check day
        day = row[3].strftime("%x")
        if day == today:
            queries_today = queries_today + 1

        # check month
        month = row[3].strftime("%m")
        if month == t_month:
            queries_monthly = queries_monthly + 1

        # 

    # seat header data:
    header_data = {
        "daily": queries_today,
        "monthly": queries_monthly
    }
        
    conn.close()

    return render_template("data.html", data=data, header_data=header_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
