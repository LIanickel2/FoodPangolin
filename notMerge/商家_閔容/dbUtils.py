import mysql.connector

# 資料庫連線設定
try:
    conn = mysql.connector.connect(
        user="root",
        password="",
        host="localhost",
        port=3306,
        database="restaurant"
    )
    cursor = conn.cursor(dictionary=True)
except mysql.connector.Error as e:
    print("資料庫連線失敗:", e)
    exit(1)

# 獲取所有菜單項目
def get_menu_items():
    sql = "SELECT * FROM menu"
    cursor.execute(sql)
    return cursor.fetchall()

# 新增菜單項目
def add_menu_item(name, price):
    sql = "INSERT INTO menu (name, price) VALUES (%s, %s)"
    params = (name, price)
    cursor.execute(sql, params)
    conn.commit()
    return cursor.lastrowid

# 刪除菜單項目
def delete_menu_item(item_id):
    sql = "DELETE FROM menu WHERE id = %s"
    params = (item_id,)
    cursor.execute(sql, params)
    conn.commit()
    return cursor.rowcount

# 獲取所有訂單
def get_orders():
    sql = "SELECT * FROM orders"
    cursor.execute(sql)
    return cursor.fetchall()

# 確認訂單
def confirm_order(order_id):
    sql = "UPDATE orders SET status = %s WHERE id = %s"
    params = ("已確認", order_id)
    cursor.execute(sql, params)
    conn.commit()
    return cursor.rowcount

# 通知取餐
def notify_pickup(order_id):
    sql = "UPDATE orders SET status = %s WHERE id = %s"
    params = ("已通知取餐", order_id)
    cursor.execute(sql, params)
    conn.commit()
    return cursor.rowcount
