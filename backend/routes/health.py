"""Health-check endpoint."""
from flask import Blueprint, jsonify

from db import query_one

health_bp = Blueprint("health", __name__, url_prefix="/api")


@health_bp.get("/health")
def health():
    try:
        row = query_one("SELECT COUNT(*) AS sale_items FROM sale_items")
        return jsonify({"status": "ok", "database": "connected", "sale_items": row["sale_items"]})
    except Exception:
        return jsonify({"status": "error", "database": "unavailable"}), 503