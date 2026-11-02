"""Sales list (with filters) and dropdown data endpoints."""
from datetime import date
from decimal import Decimal

from flask import Blueprint, jsonify, request

from db import query_all, query_one, transaction

sales_bp = Blueprint("sales", __name__, url_prefix="/api")

REVENUE_SQL = "si.quantity * si.unit_price * (1 - si.discount_rate)"


def to_json(rows):
    """Flask sends Decimal as text, so convert it to float first."""
    return [
        {k: float(v) if isinstance(v, Decimal) else v for k, v in r.items()}
        for r in rows
    ]


@sales_bp.get("/sales")
def list_sales():
    q = request.args.get("q", "").strip()
    date_from = request.args.get("date_from", "").strip()
    date_to = request.args.get("date_to", "").strip()
    # category may be one name or several separated by commas
    categories = [c.strip() for c in request.args.get("category", "").split(",") if c.strip()]

    conditions = []
    params = []
    if q:
        conditions.append("(c.full_name LIKE %s OR p.product_name LIKE %s)")
        params += ["%" + q + "%", "%" + q + "%"]
    if date_from:
        conditions.append("s.sale_date >= %s")
        params.append(date_from)
    if date_to:
        conditions.append("s.sale_date <= %s")
        params.append(date_to)
    if categories:
        placeholders = ", ".join(["%s"] * len(categories))
        conditions.append("p.category IN (" + placeholders + ")")
        params += categories

    where = "WHERE " + " AND ".join(conditions) if conditions else ""

    rows = query_all(
        f"""
        SELECT
            s.sale_id,
            CAST(s.sale_date AS CHAR) AS sale_date,
            c.full_name               AS customer,
            p.product_name            AS product,
            p.category                AS category,
            si.quantity,
            si.unit_price,
            si.discount_rate,
            ROUND({REVENUE_SQL}, 2)   AS revenue,
            s.payment_method
        FROM sale_items si
        INNER JOIN sales s     ON s.sale_id = si.sale_id
        INNER JOIN customers c ON c.customer_id = s.customer_id
        INNER JOIN products p  ON p.product_id = si.product_id
        {where}
        ORDER BY s.sale_date DESC, s.sale_id DESC
        """,
        params,
    )
    return jsonify(to_json(rows))


@sales_bp.get("/products")
def list_products():
    rows = query_all(
        "SELECT product_id, product_name, category, unit_price "
        "FROM products ORDER BY product_name"
    )
    return jsonify(to_json(rows))


@sales_bp.get("/customers")
def list_customers():
    rows = query_all(
        "SELECT customer_id, full_name FROM customers ORDER BY full_name"
    )
    return jsonify(to_json(rows))


@sales_bp.get("/categories")
def list_categories():
    rows = query_all("SELECT DISTINCT category FROM products ORDER BY category")
    return jsonify([r["category"] for r in rows])


@sales_bp.post("/sales")
def create_sale():
    data = request.get_json(silent=True) or {}

    customer_id = data.get("customer_id")
    product_id = data.get("product_id")
    quantity = data.get("quantity")
    discount_rate = data.get("discount_rate", 0)
    payment_method = (data.get("payment_method") or "Cash").strip()
    sale_date = data.get("sale_date") or date.today().isoformat()

    # --- basic validation ---
    try:
        customer_id = int(customer_id)
        product_id = int(product_id)
        quantity = int(quantity)
        discount_rate = float(discount_rate)
    except (TypeError, ValueError):
        return jsonify({"error": "Bad Request",
                        "message": "customer, product and quantity are required numbers."}), 400

    if quantity < 1:
        return jsonify({"error": "Bad Request", "message": "Quantity must be at least 1."}), 400
    if not 0 <= discount_rate <= 1:
        return jsonify({"error": "Bad Request", "message": "Discount must be between 0 and 1."}), 400

    # --- the price always comes from the products table, never from the client ---
    product = query_one("SELECT unit_price FROM products WHERE product_id = %s", [product_id])
    if not product:
        return jsonify({"error": "Bad Request", "message": "Product not found."}), 400
    customer = query_one("SELECT customer_id FROM customers WHERE customer_id = %s", [customer_id])
    if not customer:
        return jsonify({"error": "Bad Request", "message": "Customer not found."}), 400

    # --- header + line item together, or neither ---
    with transaction() as cur:
        cur.execute(
            "INSERT INTO sales (customer_id, sale_date, payment_method) VALUES (%s, %s, %s)",
            (customer_id, sale_date, payment_method),
        )
        sale_id = cur.lastrowid
        cur.execute(
            "INSERT INTO sale_items (sale_id, product_id, quantity, unit_price, discount_rate) "
            "VALUES (%s, %s, %s, %s, %s)",
            (sale_id, product_id, quantity, product["unit_price"], discount_rate),
        )

    return jsonify({"message": "Sale created", "sale_id": sale_id}), 201