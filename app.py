from flask import Flask, render_template, redirect, url_for, flash, request, session
from db import take_order, get_rest_name, details, fooddelivered, create, go, get_my_orders

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a strong secret key

# 注册用户
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['pwd']
        if create(name, email, password):
            flash("注册成功！请登录。")
            return redirect('/login')
        else:
            flash("注册失败，请重试。")
            return redirect('/register')
    return render_template('register.html')

# 登录用户
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['pwd']
        user = go(email, password)
        if user:
            session['user_id'] = user['id']
            flash("登录成功！")
            return redirect('/index')
        else:
            flash("登录失败，请重试。")
            return redirect('/login')
    return render_template('login.html')

# 主页面，显示所有待接订单和我的订单
@app.route("/index", methods=['GET', 'POST'])
def index():
    all_orders = get_rest_name()  
    user_id = session.get('user_id')
    my_orders = get_my_orders(user_id) if user_id else []
    return render_template("index.html", all_orders=all_orders, my_orders=my_orders)

# 接单操作
@app.route("/take_order/<int:order_id>", methods=["POST"])
def take_order_route(order_id):
    user_id = session.get('user_id')
    if user_id:
        success = take_order(order_id, user_id)
        if success:
            flash("接单成功")
            return redirect(url_for('order_details', order_id=order_id))  # 跳转到订单详情页面
        else:
            flash("接单失败，请重试")
    return redirect(url_for('index'))

# 订单详情页
@app.route("/order_details/<int:order_id>")
def order_details(order_id):
    order_info = details(order_id)
    return render_template("details.html", order_info=order_info)

# 标记订单已送达
@app.route("/food_delivered/<int:order_id>", methods=["POST"])
def food_delivered_route(order_id):
    if fooddelivered(order_id):
        flash("訂單已標記為已送達")
    else:
        flash("更新訂單狀態失敗")
    return redirect("/index")

# 登出操作
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    (session.clear)
    flash("您已登出。")
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
