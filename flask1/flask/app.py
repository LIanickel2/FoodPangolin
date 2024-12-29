from flask import Flask, render_template, request, session, redirect
from functools import wraps
from dbUtils import get_menu_items, add_menu_item, delete_menu_item, get_orders, confirm_order, notify_pickup

app = Flask(__name__, static_folder='static', static_url_path='/')
app.config['SECRET_KEY'] = '123TyU%^&'

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        loginID = session.get('loginID')
        if not loginID:
            return redirect('/login')
        return f(*args, **kwargs)
    return wrapper

@app.route("/menu")
# @login_required
def view_menu():
    menu = get_menu_items()
    return render_template('menu.html', data=menu)

@app.route("/addMenuItem", methods=['GET', 'POST'])
# @login_required
def add_menu_item_view():
    if request.method == 'POST':
        form = request.form
        item_name = form['name']
        item_price = form['price']
        add_menu_item(item_name, item_price)
        return redirect('/menu')
    return render_template('addMenuItem.html')

@app.route("/deleteMenuItem", methods=['POST'])
# @login_required
def delete_menu_item_view():
    item_id = request.form['item_id']
    delete_menu_item(item_id)
    return redirect('/menu')

@app.route("/orders")
# @login_required
def view_orders():
    orders = get_orders()
    return render_template('orders.html', data=orders)

@app.route("/confirmOrder", methods=['POST'])
# @login_required
def confirm_order_view():
    order_id = request.form['order_id']
    confirm_order(order_id)
    return redirect('/orders')

@app.route("/notifyPickup", methods=['POST'])
# @login_required
def notify_pickup_view():
    order_id = request.form['order_id']
    notify_pickup(order_id)
    return redirect('/orders')

if __name__ == "__main__":
    app.run(debug=True)
