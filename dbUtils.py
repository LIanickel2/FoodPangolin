import mysql.connector
from datetime import datetime

# 取得各種格式的現在時間
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
aboutTime = {
    "getCurrentTime": getCurrentTime,
    "getCurrentTime_forSQL_withHour": getCurrentTime_forSQL_withHour,
    "getCurrentTime_forSQL": getCurrentTime_forSQL,
}

# 取得資料庫連線
def get_db_connection3():
    try:
        conn = mysql.connector.connect(
            user="root",
            password="",
            host="localhost",
            port=3306,
            database="restaurant_db"
        )
        cursor = conn.cursor(dictionary=True)
        return conn, cursor
    except mysql.connector.Error as e:
        print(f"資料庫連線錯誤：{e}")
        return None, None

# 關閉資料庫連線
def close_db_connection(conn, cursor):
    if cursor:
        cursor.close()
    if conn:
        conn.close()

# 查詢單筆資料
def fetch_one(query, params=None):
    conn, cursor = get_db_connection()
    if not conn:
        return None
    try:
        cursor.execute(query, params or ())
        result = cursor.fetchone()
        return result
    except mysql.connector.Error as e:
        print(f"查詢錯誤：{e}")
        return None
    finally:
        close_db_connection(conn, cursor)

# 查詢多筆資料
def fetch_all(query, params=None):
    conn, cursor = get_db_connection()
    if not conn:
        return []
    try:
        cursor.execute(query, params or ())
        results = cursor.fetchall()
        return results
    except mysql.connector.Error as e:
        print(f"查詢錯誤：{e}")
        return []
    finally:
        close_db_connection(conn, cursor)

# 執行更新或插入操作
def execute_query(query, params=None):
    conn, cursor = get_db_connection()
    if not conn:
        return False
    try:
        cursor.execute(query, params or ())
        conn.commit()
        return True
    except mysql.connector.Error as e:
        print(f"執行錯誤：{e}")
        return False
    finally:
        close_db_connection(conn, cursor)

# 批次執行多條SQL語句
def execute_many(query, params_list):
    conn, cursor = get_db_connection()
    if not conn:
        return False
    try:
        cursor.executemany(query, params_list)
        conn.commit()
        return True
    except mysql.connector.Error as e:
        print(f"批次執行錯誤：{e}")
        return False
    finally:
        close_db_connection(conn, cursor)

# 取得特定使用者資訊
def get_user_by_username(user_id):
    return fetch_one("SELECT * FROM users WHERE user_id = %s", (user_id,))

# 新增使用者
def create_user(user_id, password, role, register_time, last_login_time):
    query = "INSERT INTO users (user_id, password, role, register_time, last_login_time) VALUES (%s, %s, %s, %s, %s)"
    return execute_query(query, (user_id, password, role, register_time, last_login_time))

# 更新使用者上次登入時間
def update_last_login_time(user_id, last_login_time):
    query = "UPDATE users SET last_login_time = %s WHERE id = %s"
    return execute_query(query, (last_login_time, user_id))


# # 取得所有使用者帳號
# def get_all_username():
#     query = "SELECT * FROM users"
#     return fetch_all(query)

# 餐廳菜單相關操作
# 查詢餐廳的所有菜單項目
def get_menu_items(restaurant_id):
    query = "SELECT * FROM menu_items WHERE restaurant_id = %s AND available = TRUE"
    return fetch_all(query, (restaurant_id,))

# 新增菜單項目
def create_menu_item(restaurant_id, name, description, price):
    query = "INSERT INTO menu_items (restaurant_id, name, description, price) VALUES (%s, %s, %s, %s)"
    return execute_query(query, (restaurant_id, name, description, price))

# 訂單相關操作
# 查詢客戶的訂單
def get_customer_orders(customer_id):
    query = "SELECT * FROM orders WHERE customer_id = %s"
    return fetch_all(query, (customer_id,))

# 新增訂單
def create_order(customer_id, restaurant_id, total_amount):
    query = "INSERT INTO orders (customer_id, restaurant_id, total_amount) VALUES (%s, %s, %s)"
    return execute_query(query, (customer_id, restaurant_id, total_amount))

# 更新訂單狀態
def update_order_status(order_id, status):
    query = "UPDATE orders SET status = %s WHERE id = %s"
    return execute_query(query, (status, order_id))

# 結算相關操作
# 查詢結算記錄
def get_settlements():
    query = "SELECT * FROM settlements"
    return fetch_all(query)

# 新增結算記錄
def create_settlement(user_id, role, amount):
    query = "INSERT INTO settlements (user_id, role, amount) VALUES (%s, %s, %s)"
    return execute_query(query, (user_id, role, amount))
