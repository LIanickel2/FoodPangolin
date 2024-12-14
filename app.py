# Flask 後端程式
from flask import Flask, render_template, request, redirect, session, flash, jsonify
from dbUtils import execute_query, fetch_one, fetch_all
from werkzeug.security import generate_password_hash, check_password_hash

def get_user_by_username(username):
    return fetch_one("SELECT * FROM users WHERE username = %s", (username,))

def create_user(username, password, role):
    return execute_query(
        "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
        (username, password, role)
    )

app = Flask(__name__)
app.secret_key = "your_secret_key"

# 路由設定
@app.route("/")
def home_page():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # 檢查使用者是否存在於資料庫
        user = get_user_by_username(username)

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["role"] = user["role"]
            return redirect(f"/{user['role']}/dashboard")
        else:
            flash("帳號或密碼錯誤", "danger")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])
        role = request.form["role"]

        # 新增使用者至資料庫
        create_user(username, password, role)

        flash("註冊成功", "success")
        return redirect("/login")

    return render_template("register.html")

# 餐廳商家儀表板
@app.route("/restaurant/dashboard")
def restaurant_dashboard():
    if session.get("role") != "restaurant":
        return redirect("/")
    return render_template("restaurant_dashboard.html")

# 送貨小哥儀表板
@app.route("/delivery/dashboard")
def delivery_dashboard():
    if session.get("role") != "delivery":
        return redirect("/")
    return render_template("delivery_dashboard.html")

# 客戶儀表板
@app.route("/customer/dashboard")
def customer_dashboard():
    if session.get("role") != "customer":
        return redirect("/")
    return render_template("customer_dashboard.html")

# 平台結算功能
@app.route("/platform/settlement")
def platform_settlement():
    if session.get("role") != "admin":
        return redirect("/")
    # 執行結算邏輯
    return render_template("settlement.html")

if __name__ == "__main__":
    app.run(debug=True)
