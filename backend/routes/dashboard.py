"""Dashboard endpoints: KPI stats and chart data.

Revenue convention: quantity * unit_price * (1 - discount_rate),
always computed in SQL (never in Python or the frontend).
"""
from decimal import Decimal

from flask import Blueprint, jsonify

from db import query_all, query_one

dashboard_bp = Blueprint("dashboard", __name__)

# Single source of truth for the revenue formula used by every query here.
REVENUE_SQL = "si.quantity * si.unit_price * (1 - si.discount_rate)"


def _num(value, default=0.0):
    """Convert Decimal/None from MySQL into a JSON-friendly float."""
    if value is None:
        return default
    if isinstance(value, Decimal):
        return float(value)
    return value


@dashboard_bp.get("/api/stats")
def get_stats():
    row = query_one(
        f"""
        SELECT
            COALESCE(SUM({REVENUE_SQL}), 0)                       AS total_revenue,
            COUNT(DISTINCT si.sale_id)                            AS total_orders,
            COALESCE(SUM(si.quantity), 0)                         AS total_units,
            COALESCE(SUM({REVENUE_SQL})
                     / NULLIF(COUNT(DISTINCT si.sale_id), 0), 0)  AS avg_order_value
        FROM sale_items si
        """
    )
    return jsonify(
        {
            "total_revenue": round(_num(row["total_revenue"]), 2),
            "total_orders": int(row["total_orders"]),
            "total_units": int(row["total_units"]),
            "avg_order_value": round(_num(row["avg_order_value"]), 2),
        }
    )


@dashboard_bp.get("/api/charts/monthly-revenue")
def monthly_revenue():
    rows = query_all(
        f"""
        SELECT
            CONCAT(YEAR(s.sale_date), '-', LPAD(MONTH(s.sale_date), 2, '0')) AS month,
            ROUND(SUM({REVENUE_SQL}), 2) AS revenue
        FROM sales s
        INNER JOIN sale_items si ON si.sale_id = s.sale_id
        GROUP BY month
        ORDER BY month
        """
    )
    return jsonify(
        {
            "labels": [r["month"] for r in rows],
            "values": [_num(r["revenue"]) for r in rows],
        }
    )


@dashboard_bp.get("/api/charts/category-sales")
def category_sales():
    rows = query_all(
        f"""
        SELECT
            p.category                   AS category,
            ROUND(SUM({REVENUE_SQL}), 2) AS revenue
        FROM sale_items si
        INNER JOIN products p ON p.product_id = si.product_id
        GROUP BY p.category
        ORDER BY revenue DESC
        """
    )
    return jsonify(
        {
            "labels": [r["category"] for r in rows],
            "values": [_num(r["revenue"]) for r in rows],
        }
    )