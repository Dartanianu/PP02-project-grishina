from database.connection import DatabaseError, fetch_all, fetch_one, run_in_trans

USER_NAME = "u.last_name || ' ' || u.first_name || ' ' || u.second_name"

def create_order(user_id, cart_items, status_id):
    def action(cursor):
        cursor.execute(
            "INSERT INTO orders (order_date, user_id, status) VALUES (CURRENT_DATE, %s, %s) RETURNING order_id",
            (user_id, status_id)
        )
        order_id = cursor.fetchone()["order_id"]
        
        for item in cart_items:
            cursor.execute("""
                UPDATE stock_items
                SET quantity = quantity - %s
                WHERE product_id = %s AND variation_id = %s AND quantity >= %s
            """, (item['quantity'], item['product_id'], item['variation_id'], item['quantity']),
            )
            if cursor.rowcount == 0:
                raise DatabaseError(
                    f"Недостаточно товара «{item['product_name']}» размера {item['variation_name']} на складе."
                )
            cursor.execute("""
                INSERT INTO order_items (order_id, product_id, variation_id, quantity, price)
                VALUES (%s, %s, %s, %s, %s)
            """, (order_id, item['product_id'], item['variation_id'], item['quantity'], item['price']),)
            
        return order_id
        
    return run_in_trans(action)

def get_orders():
    return fetch_all(f"""
        SELECT o.order_id, o.order_date, {USER_NAME} AS client_name, s.name AS status,
                    COALESCE(SUM(oi.quantity * oi.price), 0) AS total_sum
        FROM orders o
        JOIN users u ON o.user_id = u.user_id
        JOIN status s ON o.status = s.id
        LEFT JOIN order_items oi ON oi.order_id = o.order_id
        GROUP BY o.order_id, u.user_id, s.name
        ORDER BY o.order_date DESC, o.order_id DESC 
    """)

def get_status():
    return fetch_all("""
    SELECT id, name FROM status
    """)

def get_order_by_id(oder_id):
    return fetch_one(f"""
        SELECT o.order_id, o.order_date, {USER_NAME} AS client_name
        FROM orders o
        JOIN users u ON o.user_id = u.user_id
        WHERE o.order_id = %s
    """, (oder_id,))

def get_order_items(order_id):
    return fetch_all("""
        SELECT oi.order_item_id, p.name AS product_name, man.name AS manufacturer, v.name AS variation,
                     oi.quantity, oi.price
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        JOIN product_variation v ON oi.variation_id = v.variation_id
        JOIN manufactures man ON man.manufacture_id = p.manufacture_id
        WHERE oi.order_id = %s
        ORDER BY oi.order_item_id
    """, (order_id,))

def _return_item_order(cursor, cond_sql, params):
    cursor.execute(
        f"""
        UPDATE stock_items st
        SET quantity = st.quantity + oi.quantity
        FROM order_items oi
        WHERE st.product_id = oi.product_id
            AND st.variation_id = oi.variation_id
            AND {cond_sql}
    """,
    params)

def delete_order(order_id):
    def action(cursor):
        _return_item_order(cursor, "oi.order_id = %s", (order_id,))
        cursor.execute("DELETE FROM orders WHERE order_id = %s", (order_id,))
        if cursor.rowcount == 0:
            raise DatabaseError(f"Заказ №{order_id} не найден. Возможно, он уже удален.")
        
    run_in_trans(action)

def update_order(order_id, new_date, removed_item_ids):
    def action(cursor):
        for order_item_id in removed_item_ids:
            _return_item_order(cursor, "oi.order_item_id = %s", (order_item_id,))
            cursor.execute("DELETE FROM order_items WHERE order_item_id = %s", (order_item_id,))
        cursor.execute("UPDATE orders SET order_date = %s WHERE order_id = %s", (new_date, order_id))
    run_in_trans(action)