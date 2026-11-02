"""Quick connection check. Run once, then ignore."""
import pymysql

from config import Config


def main():
    conn = pymysql.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        cursorclass=pymysql.cursors.DictCursor,
    )
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT VERSION() AS version, CURRENT_USER() AS user, DATABASE() AS db")
            print(cur.fetchone())
            cur.execute("SELECT COUNT(*) AS items FROM sale_items")
            print(cur.fetchone())
    finally:
        conn.close()


if __name__ == "__main__":
    main()