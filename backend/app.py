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

if __name__ == "__main__":
    app.run(debug=True)