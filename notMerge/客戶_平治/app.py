from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # 請替換為你的 MySQL 密碼
    'database': 'delivery_platform'
}

# Database connection
def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/restaurants')
def restaurants():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM restaurants")
    data = cursor.fetchall()
    conn.close()
    return render_template('restaurants.html', restaurants=data)

@app.route('/menu/<int:restaurant_id>')
def menu(restaurant_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 獲取餐廳名稱
    cursor.execute("SELECT id, name FROM restaurants WHERE id = %s", (restaurant_id,))
    restaurant = cursor.fetchone()
    
    # 獲取菜單
    cursor.execute("SELECT id, name, price FROM foods WHERE restaurant_id = %s", (restaurant_id,))
    menu_items = cursor.fetchall()
    
    conn.close()
    return render_template('menu.html', restaurant=restaurant, menu_items=menu_items)


@app.route('/add_to_cart/<int:food_id>/<int:restaurant_id>')
def add_to_cart(food_id, restaurant_id):
    user_id = 1  # 假設用戶 ID 是 1，實際應從會話中獲取
    quantity = 1  # 預設數量為 1，或者根據需要修改

    # 添加菜品到購物車的邏輯
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO cart (user_id, food_id, quantity) VALUES (%s, %s, %s)",
        (user_id, food_id, quantity)
    )
    conn.commit()
    conn.close()

    # 跳回菜單頁面
    return redirect(f'/menu/{restaurant_id}')


@app.route('/cart')
def cart():
    user_id = 1  # 假設用戶 ID 是 1
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 查詢購物車內容
    cursor.execute("""
        SELECT c.id, f.name, c.quantity, f.price, (c.quantity * f.price) AS total_price
        FROM cart c
        JOIN foods f ON c.food_id = f.id
        WHERE c.user_id = %s
    """, (user_id,))
    cart_items = cursor.fetchall()

    # 計算總金額
    total_amount = sum(item['total_price'] for item in cart_items)

    # 關閉連線
    cursor.close()
    conn.close()

    return render_template('cart.html', cart_items=cart_items, total_amount=total_amount)



@app.route('/place_order', methods=['POST'])
def place_order():
    user_id = 1  # 假設用戶 ID 是 1
    total_amount = request.form['total_amount']  # 假設金額是從表單提交過來的

    conn = get_db_connection()
    cursor = conn.cursor()

    # 插入訂單資料
    cursor.execute("""
        INSERT INTO orders (user_id, total_amount, status)
        VALUES (%s, %s, '待處理')
    """, (user_id, total_amount))

    # 確認訂單 ID
    order_id = cursor.lastrowid
    conn.commit()

    # 關閉連線
    cursor.close()
    conn.close()

    return redirect(f'/shipping/{order_id}')




@app.route('/shipping/<int:order_id>', methods=['GET', 'POST'])
def shipping(order_id):
    # 獲取訂單資訊
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 如果是 GET 請求，顯示訂單詳細資訊
    if request.method == 'GET':
        cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
        order = cursor.fetchone()

        conn.close()
        return render_template('shipping.html', order_id=order_id,order_status=order['status'])

    # 如果是 POST 請求，表示確認收貨或提交評價
    elif request.method == 'POST':
        # 更新訂單狀態為已收貨
        cursor.execute("""
            UPDATE orders
            SET status = '已收貨'
            WHERE id = %s
        """, (order_id,))
        conn.commit()

        # 如果有提交評價，則保存評價
        review_text = request.form.get('review_text')
        rating = request.form.get('rating')

        if review_text and rating:
            cursor.execute("""
                INSERT INTO reviews (order_id, review_text, rating)
                VALUES (%s, %s, %s)
            """, (order_id, review_text, rating))
            conn.commit()


            # 清空購物車
        user_id = 1  # 假設用戶 ID 是 1，實際應從會話中獲取
        cursor.execute("DELETE FROM cart WHERE user_id = %s", (user_id,))
        conn.commit()

        conn.close()

        return redirect(f'/shipping/{order_id}')  # 確認收貨後跳轉至餐廳列表



@app.route('/cart/delete/<int:cart_item_id>', methods=['POST'])
def delete_from_cart(cart_item_id):
    """
    刪除購物車中的指定菜品
    """
    
    conn = get_db_connection()
    cursor = conn.cursor()

        # 刪除指定的購物車項目
    cursor.execute("DELETE FROM cart WHERE id = %s", (cart_item_id,))
    conn.commit()

    cursor.close()
    conn.close()
    return redirect('/cart')
    
























@app.route('/test_db')
def test_db():
    try:
        # 連接資料庫
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DATABASE()")  # 確認目前使用的資料庫
        db_name = cursor.fetchone()
        conn.close()
        return f"成功連接到資料庫: {db_name[0]}"
    except Exception as e:
        return f"資料庫連接失敗: {str(e)}"





if __name__ == '__main__':
    app.run(debug=True)
