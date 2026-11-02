"""Add new customers and products."""
import pymysql
from flask import Blueprint, jsonify, request

from db import query_one, transaction

master_bp = Blueprint("master", __name__, url_prefix="/api")


def bad(message):
    return jsonify({"error": "Bad Request", "message": message}), 400


@master_bp.post("/customers")
def create_customer():
    data = request.get_json(silent=True) or {}
    full_name = (data.get("full_name") or "").strip()
    email = (data.get("email") or "").strip()
    city = (data.get("city") or "").strip()
    state = (data.get("state") or "").strip()

    if not full_name:
        return bad("Full name is required.")
    if len(full_name) > 100:
        return bad("Full name is too long (max 100).")
    if "@" not in email or "." not in email:
        return bad("A valid email is required.")
    if len(email) > 120:
        return bad("Email is too long (max 120).")
    if not city or not state:
        return bad("City and state are required.")
    if len(city) > 60 or len(state) > 60:
        return bad("City or state is too long (max 60).")

    if query_one("SELECT customer_id FROM customers WHERE email = %s", [email]):
        return bad("A customer with this email already exists.")

    try:
        with transaction() as cur:
            cur.execute(
                "INSERT INTO customers (full_name, email, city, state) VALUES (%s, %s, %s, %s)",
                (full_name, email, city, state),
            )
            customer_id = cur.lastrowid
    except pymysql.err.IntegrityError:
        return bad("Could not save: the details clash with an existing customer.")

    return jsonify({"message": "Customer created", "customer_id": customer_id}), 201


@master_bp.post("/products")
def create_product():
    data = request.get_json(silent=True) or {}
    product_name = (data.get("product_name") or "").strip()
    category = (data.get("category") or "").strip()

    try:
        unit_price = float(data.get("unit_price"))
    except (TypeError, ValueError):
        return bad("Price must be a number.")

    if not product_name or not category:
        return bad("Product name and category are required.")
    if len(product_name) > 100 or len(category) > 50:
        return bad("Product name (max 100) or category (max 50) is too long.")
    if unit_price <= 0 or unit_price >= 100000000:
        return bad("Price must be greater than 0 and below 100000000.")

    if query_one("SELECT product_id FROM products WHERE LOWER(product_name) = LOWER(%s)", [product_name]):
        return bad("A product with this name already exists.")

    try:
        with transaction() as cur:
            cur.execute(
                "INSERT INTO products (product_name, category, unit_price) VALUES (%s, %s, %s)",
                (product_name, category, round(unit_price, 2)),
            )
            product_id = cur.lastrowid
    except pymysql.err.IntegrityError:
        return bad("Could not save: the details clash with an existing product.")

    return jsonify({"message": "Product created", "product_id": product_id}), 201