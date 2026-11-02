"""Flask application entry point."""
import os

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from config import Config
from routes.health import health_bp
from routes.dashboard import dashboard_bp
from routes.sales import sales_bp
from routes.export import export_bp
from routes.master import master_bp

# backend\ is this file's folder; the frontend sits next to it
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "frontend"))


def create_app():
    # static_url_path="" serves css/style.css and js/app.js at /css/... and /js/...
    app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
    app.config.from_object(Config)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    app.register_blueprint(health_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(master_bp)

    @app.route("/")
    def index():
        return send_from_directory(FRONTEND_DIR, "index.html")

    @app.errorhandler(HTTPException)
    def handle_http_error(err):
        return jsonify({"error": err.name, "message": err.description}), err.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(err):
        app.logger.exception("Unhandled error")
        return jsonify({"error": "Internal Server Error", "message": "Something went wrong."}), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=Config.DEBUG)