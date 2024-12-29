import mysql.connector
from mysql.connector import Error

def get_db_connection():
    """建立新的 MySQL 数据库连接并返回连接和游标"""
    try:
        conn = mysql.connector.connect(
            user="root",
            password="",
            host="localhost",
            port=3306,
            database="1"  # Change this to your actual database name
        )
        cursor = conn.cursor(dictionary=True)
        print("Database connection successful")
        return conn, cursor
    except mysql.connector.Error as e:
        print(f"Error: {e}")    
        return None, None

def take_order(order_id, user_id):
    """接單，將訂單狀態更新為已分配"""
    conn, cursor = get_db_connection()
    if conn is None:
        print("连接错误，無法接單。")
        return False
    try:
        sql = """
            UPDATE orders SET status = '已分配' ,delivery_person_id = %s 
            WHERE id = %s AND delivery_person_id IS NULL
        """
        cursor.execute(sql, (user_id, order_id))  
        conn.commit()
        print(f"訂單 {order_id} 接單成功！")
        return True
    except Exception as e:
        print(f"接單失敗：{e}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_rest_name(): 
    """獲取所有待分配訂單的餐廳名稱"""
    conn, cursor = get_db_connection()
    if conn is None:
        print("无法连接到数据库")
        return []
    try:
        sql = """
            SELECT orders.id AS order_id, rest.rest_name
            FROM orders
            JOIN rest ON orders.rest_id = rest.id
            WHERE orders.status = '未分配'
        """
        cursor.execute(sql)
        results = cursor.fetchall()
        return results
    except Exception as e:
        print(f"查询餐厅名称失败：{e}")
        return []
    finally:
        cursor.close()
        conn.close()

def details(order_id):
    """根据订单ID查询订单详情（商品名称、价格和状态）"""
    conn, cursor = get_db_connection()
    if conn is None:
        print("连接错误，无法查看订单内容。")
        return []
    try:
        sql = """
        SELECT 
        orders.id AS order_id, 
        rest.rest_name, 
        orders.status, 
        menu.name AS product_name, 
        menu.price, 
        order_items.quantity
        FROM orders
        JOIN rest ON orders.rest_id = rest.id
        JOIN order_items ON orders.id = order_items.order_id
        JOIN menu ON order_items.menu_id = menu.id
        WHERE orders.id = %s
        """
        cursor.execute(sql, (order_id,))
        results = cursor.fetchall()
        return results
    except Exception as e:
        print(f"查询订单详情失败: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def fooddelivered(order_id):
    """标记订单为已送达"""
    conn, cursor = get_db_connection()
    if conn is None:
        print("连接错误，无法查看訂單内容。")
        return False
    try:
        sql = "UPDATE orders SET status = '已送達' WHERE id = %s"
        cursor.execute(sql, (order_id,))
        conn.commit()
        print(f"訂單 {order_id} 已標記為已送達！")
        return True
    except Exception as e:
        print(f"更新订单状态失败：{e}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_my_orders(user_id):
    """根據外送員ID查詢所有已接的訂單"""
    conn, cursor = get_db_connection()
    if conn is None:
        print("连接错误，无法查询我的订单。")
        return []
    try:
        sql = """
        SELECT orders.id AS order_id, rest.rest_name, orders.status, menu.name AS product_name, menu.price
        FROM orders
        JOIN rest ON orders.rest_id = rest.id
        JOIN order_items ON orders.id = order_items.order_id
        JOIN menu ON order_items.menu_id = menu.id
        WHERE orders.delivery_person_id = %s AND orders.status IN ('已分配', '未送達')
        """
        cursor.execute(sql, (user_id,))
        results = cursor.fetchall()
        return results if results else []  # 确保返回空列表而不是 None
    except Exception as e:
        print(f"查询我的订单失败: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def create(name, email, password):
    conn, cursor = get_db_connection()
    if conn is None:
        print("连接错误，无法创建用户。")
        return False
    try:
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        if cursor.fetchone():  
            print(f"Email {email} already registered.")
            return False
        sql = """
        INSERT INTO users (name, email, password) VALUES (%s, %s, %s)
        """
        cursor.execute(sql, (name, email, password))
        conn.commit()
        print(f"User {name} with email {email} created successfully!")
        return True
    except Exception as e:
        print(f"创建賬號失敗: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def go(email, password):
    conn, cursor = get_db_connection()
    if conn is None:
        print("连接错误，无法查看訂單内容。")
        return False
    try:
        sql = """
        SELECT * FROM users WHERE email = %s AND password = %s
        """
        cursor.execute(sql, (email, password))
        result = cursor.fetchone()
        return result
    except Exception as e:
        print(f"登入失敗: {e}")
        return False
    finally:
        cursor.close()
        conn.close()
