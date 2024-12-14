# Flask 後端程式
from flask import Flask, render_template, request, redirect, session, flash, jsonify, url_for
from dbUtils import execute_query, fetch_one, fetch_all, get_user_by_username, create_user, update_last_login_time
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
from datetime import datetime

# 取得各種格式的現在時間
class AboutTime:
    def getCurrentTime():
        now = datetime.now()
        year, month, day, weekday_number, hour, minute, second = \
        now.year, now.month, now.day, now.weekday(), now.hour, now.minute, now.second
        weekdays = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
        weekday = weekdays[weekday_number]
        return f"{year}年{month}月{day}日，{weekday}，{hour}點{minute}分{second}秒"
    def getCurrentTime_forSQL_withHour():
        now = datetime.now()
        now_str = now.strftime('%Y-%m-%d %H:%M:%S')
        return now_str
    def getCurrentTime_forSQL():
        now = datetime.now()
        now_str = now.strftime('%Y-%m-%d')
        return now_str

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

# 未登入首頁
@app.route("/")
def not_login_page():
    return render_template("NotLoginPage.html")

# 登入頁面
@app.route('/loginPage')
def login_page():
    role = request.args.get('role')  # 獲取 URL 中的 role 參數
    if role not in ['customer', 'restaurant', 'delivery']:
        return redirect(url_for('not_login_page'))  # 如果角色無效，重定向到首頁
    return render_template('loginPage.html', role=role)  # 傳遞角色到登入頁面

# 處理登入請求
@app.route("/login", methods=["POST"])
def login():
    # 接收使用者的輸入
    user_id = request.form["username"]
    password = request.form["password"]
    role = request.form.get('role')  # 獲取表單中的角色選項

    # 檢查使用者是否存在於資料庫
    user = get_user_by_username(user_id)
    if user:
        # 檢查該用戶的角色是否與所選角色一致
        if user["role"] != role:
            # 角色不匹配，顯示錯誤訊息並重定向到註冊頁面
            error_message = f"此帳號尚未註冊成為{role}。請前往註冊頁面。"
            return render_template('loginPage.html', role=role, error=error_message)
        # 檢查輸入的密碼是否符合此帳號
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["user_id"]
            session["role"] = user["role"]
            update_last_login_time(user_id, AboutTime.getCurrentTime_forSQL_withHour())
            flash(f"歡迎回來，{user_id}", 'success')
            return redirect(f"/{role}/dashboard")
        else:
            error_message = "帳號或密碼錯誤"
            return render_template('loginPage.html', role=role, error=error_message)
    else:
        error_message = "帳號不存在，請註冊"
        return render_template('loginPage.html', role=role, error=error_message)

# 註冊頁面
@app.route('/registerPage')
def register_page():
    role = request.args.get('role')  # 獲取角色參數
    if role not in ['customer', 'restaurant', 'delivery']:
        return redirect(url_for('home'))  # 如果角色無效，返回首頁
    return render_template('registerPage.html', role=role)

# 處理註冊請求
@app.route("/register", methods=["GET", "POST"])
def register():
    user_id = request.form["username"]
    password = request.form["password"]
    role = request.form.get('role')

    # 檢查使用者是否存在於資料庫
    user = get_user_by_username(user_id)
    if not user:
        # 生成雜湊密碼
        password = generate_password_hash(password)
        # 新增使用者至資料庫
        session["user_id"] = user_id
        session["role"] = role
        create_user(user_id, password, role, AboutTime.getCurrentTime_forSQL_withHour(), AboutTime.getCurrentTime_forSQL_withHour())
        flash("註冊成功", "success")
        return redirect(f"/{role}/dashboard")
    else:
        flash('使用者名稱已被使用')
        return render_template('registerPage.html', role=role)

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

# 顧客儀表板
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

# 登出
@app.route('/logout')
def logout():
    # 清除 session 中的 loginID
    session.pop('loginID', None)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
