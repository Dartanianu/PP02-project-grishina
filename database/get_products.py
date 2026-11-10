from database.connection import fetch_all

def get_products():
    return fetch_all(
        """
        SELECT
        p.product_id,
        c.name AS category,
        subc.name AS subcategory,
        m.name AS manufacturer,
        p.name,
        p.description,
        p.compound,
        p.image_path,
        p.price,
        COALESCE(SUM(si.quantity), 0) AS total_quantity
        FROM products p
        LEFT JOIN stock_items si ON si.product_id = p.product_id
        LEFT JOIN categories c ON c.category_id = p.category_id
        LEFT JOIN subcategories subc ON subc.subcategory_id = p.subcategory_id
        LEFT JOIN manufactures m ON m.manufacture_id = p.manufacture_id
        GROUP BY p.product_id, c.name, subc.name, m.name, p.name, p.description, p.compound, p.image_path, p.price
        ORDER BY p.product_id
        """)

def get_categories():
    rows = fetch_all("SELECT DISTINCT name FROM categories ORDER BY name")
    return [row["name"] for row in rows]

def get_product_variations(product_id):
    return fetch_all(
        """
        SELECT
        v.variation_id,
        v.name,
        si.quantity AS quantity_available
        FROM stock_items si
        JOIN product_variation v ON si.variation_id = v.variation_id
        WHERE si.product_id = %s
        GROUP BY v.name, v.variation_id, si.quantity
        ORDER BY v.variation_id        
        """, (product_id,))

def get_products_id(per_start, per_end):
    rows = fetch_all("""
        SELECT DISTINCT oi.product_id
        FROM order_items oi
        JOIN orders o ON o.order_id = oi.order_id
        WHERE o.order_date >= %s AND o.order_date < %s
    """, (per_start, per_end))
    return {row["product_id"] for row in rows}