from database.connection import DatabaseError, fetch_all, fetch_one, run_in_trans

def create_order(user_id, cart_items):
    def action(cursor):
        cursor.execute(
            "INSERT INTO orders (order_date, user_id) VALUES (CURRENT_DATE, %s) RETURNING order_id",
            (user_id,)
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