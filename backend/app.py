from flask import Flask, jsonify, request
import psycopg2

app = Flask(__name__)

def get_connection():
    return psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="store",
        user="admin",
        password="admin123"
    )

@app.route("/")
def home():
    return "Store backend is running"


@app.route("/products", methods=["GET"])
def get_products():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, price, stock FROM products")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    products = []
    for row in rows:
        products.append({
            "id": row[0],
            "name": row[1],
            "price": float(row[2]),
            "stock": row[3]
        })
    return jsonify(products)


@app.route("/products", methods=["POST"])
def add_product():
    data = request.get_json()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO products (name, price, stock) VALUES (%s, %s, %s) RETURNING id",
        (data["name"], data["price"], data["stock"])
    )
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"id": new_id, "message": "Product added"}), 201


@app.route("/customers", methods=["GET"])
def get_customers():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email FROM customers")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    customers = []
    for row in rows:
        customers.append({
            "id": row[0],
            "name": row[1],
            "email": row[2]
        })
    return jsonify(customers)


@app.route("/customers", methods=["POST"])
def add_customer():
    data = request.get_json()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO customers (name, email) VALUES (%s, %s) RETURNING id",
        (data["name"], data["email"])
    )
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"id": new_id, "message": "Customer added"}), 201


@app.route("/orders", methods=["POST"])
def create_order():
    data = request.get_json()
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO orders (customer_id) VALUES (%s) RETURNING id",
        (data["customer_id"],)
    )
    order_id = cur.fetchone()[0]

    for item in data["items"]:
        cur.execute(
            "INSERT INTO order_items (order_id, product_id, quantity) VALUES (%s, %s, %s)",
            (order_id, item["product_id"], item["quantity"])
        )

    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"order_id": order_id, "message": "Order created"}), 201


@app.route("/orders", methods=["GET"])
def get_orders():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT o.id, c.name, p.name, oi.quantity, p.price
        FROM orders o
        JOIN customers c ON o.customer_id = c.id
        JOIN order_items oi ON oi.order_id = o.id
        JOIN products p ON oi.product_id = p.id
        ORDER BY o.id
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    orders = []
    for row in rows:
        orders.append({
            "order_id": row[0],
            "customer": row[1],
            "product": row[2],
            "quantity": row[3],
            "price": float(row[4])
        })
    return jsonify(orders)


if __name__ == "__main__":
    app.run(debug=True)