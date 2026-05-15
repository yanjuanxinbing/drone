import hashlib
import sqlite3
import json
import os
from file import FileReader

DB_PATH = "db/data/dronego.db"


def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _init_db():
    with _get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                phone    TEXT PRIMARY KEY,
                nick_name TEXT NOT NULL,
                password  TEXT NOT NULL,
                gender    TEXT NOT NULL DEFAULT '保密',
                birthday  TEXT NOT NULL DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS addresses (
                id         TEXT NOT NULL,
                phone      TEXT NOT NULL REFERENCES users(phone) ON DELETE CASCADE,
                address    TEXT NOT NULL,
                location   TEXT NOT NULL DEFAULT '',
                sort_order INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (id, phone)
            );

            CREATE TABLE IF NOT EXISTS orders (
                id             TEXT PRIMARY KEY,
                phone          TEXT NOT NULL REFERENCES users(phone) ON DELETE CASCADE,
                drone_id       TEXT NOT NULL DEFAULT '',
                drone_name     TEXT NOT NULL DEFAULT '',
                start_address  TEXT NOT NULL DEFAULT '',
                start_location TEXT NOT NULL DEFAULT '',
                address        TEXT NOT NULL DEFAULT '',
                location       TEXT NOT NULL DEFAULT '',
                start_time     TEXT NOT NULL DEFAULT '',
                total_price    REAL NOT NULL DEFAULT 0,
                status         TEXT NOT NULL DEFAULT '',
                created_at     TEXT NOT NULL DEFAULT '',
                is_booking     INTEGER NOT NULL DEFAULT 0
            );
        """)


def _migrate_from_json():
    """首次运行时从 users.json 导入数据"""
    raw = FileReader.read_json("users.json")
    if not raw:
        return

    with _get_conn() as conn:
        for phone, user in raw.items():
            conn.execute(
                "INSERT OR IGNORE INTO users (phone, nick_name, password, gender, birthday) VALUES (?,?,?,?,?)",
                (phone, user.get("nick_name", ""), user.get("password", ""),
                 user.get("gender", "保密"), user.get("birthday", ""))
            )

            for i, addr in enumerate(user.get("addresses", [])):
                conn.execute(
                    "INSERT OR IGNORE INTO addresses (id, phone, address, location, sort_order) VALUES (?,?,?,?,?)",
                    (addr["id"], phone, addr.get("address", ""),
                     addr.get("location", ""), i)
                )

            for order in user.get("orders", []):
                conn.execute(
                    """INSERT OR IGNORE INTO orders
                       (id, phone, drone_id, drone_name, start_address, start_location,
                        address, location, start_time, total_price, status, created_at, is_booking)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (order.get("id", ""), phone,
                     order.get("drone_id", ""), order.get("drone_name", ""),
                     order.get("start_address", ""), order.get("start_location", ""),
                     order.get("address", ""),
                     order.get("location", order.get("loaction", "")),
                     order.get("start_time", ""), order.get("total_price", 0),
                     order.get("status", ""), order.get("created_at", ""),
                     1 if order.get("is_booking") else 0)
                )

    print("UserManager: 已从 users.json 迁移数据到 SQLite")


if not os.path.exists(DB_PATH):
    _init_db()
    _migrate_from_json()
else:
    _init_db()


class UserManager:
    def __init__(self):
        pass

    def _hash_password(self, password: str) -> str:
        sha256 = hashlib.sha256()
        sha256.update(password.encode("utf-8"))
        return sha256.hexdigest()

    def get(self, phone) -> dict | None:
        with _get_conn() as conn:
            row = conn.execute("SELECT * FROM users WHERE phone=?", (phone,)).fetchone()
            if not row:
                return None
            return {
                "nick_name": row["nick_name"],
                "password":  row["password"],
                "gender":    row["gender"],
                "birthday":  row["birthday"],
                "addresses": self.get_addresses(phone),
                "orders":    self.get_orders(phone),
            }

    def get_addresses(self, phone: str) -> list:
        with _get_conn() as conn:
            rows = conn.execute(
                "SELECT id, address, location FROM addresses WHERE phone=? ORDER BY sort_order ASC",
                (phone,)
            ).fetchall()
            return [{"id": r["id"], "address": r["address"], "location": r["location"]} for r in rows]

    def get_location_by_address(self, phone: str, address: str) -> str:
        with _get_conn() as conn:
            row = conn.execute(
                "SELECT location FROM addresses WHERE phone=? AND address=?",
                (phone, address)
            ).fetchone()
            return row["location"] if row else ""

    def add_address(self, phone: str, address: str, location: str):
        with _get_conn() as conn:
            max_row = conn.execute(
                "SELECT MAX(CAST(id AS INTEGER)) as max_id, MAX(sort_order) as max_order FROM addresses WHERE phone=?",
                (phone,)
            ).fetchone()
            new_id = str((max_row["max_id"] or 0) + 1)
            new_order = (max_row["max_order"] or -1) + 1
            conn.execute(
                "INSERT INTO addresses (id, phone, address, location, sort_order) VALUES (?,?,?,?,?)",
                (new_id, phone, address, location, new_order)
            )

    def update_address(self, phone: str, addr_id: str, address: str, location: str):
        with _get_conn() as conn:
            conn.execute(
                "UPDATE addresses SET address=?, location=? WHERE phone=? AND id=?",
                (address, location, phone, addr_id)
            )

    def set_default_address(self, phone: str, addr_id: str):
        with _get_conn() as conn:
            first = conn.execute(
                "SELECT id FROM addresses WHERE phone=? ORDER BY sort_order ASC LIMIT 1",
                (phone,)
            ).fetchone()
            if not first or first["id"] == addr_id:
                return
            first_id = first["id"]
            order_a = conn.execute(
                "SELECT sort_order FROM addresses WHERE phone=? AND id=?", (phone, first_id)
            ).fetchone()["sort_order"]
            order_b = conn.execute(
                "SELECT sort_order FROM addresses WHERE phone=? AND id=?", (phone, addr_id)
            ).fetchone()["sort_order"]
            conn.execute("UPDATE addresses SET sort_order=? WHERE phone=? AND id=?", (order_b, phone, first_id))
            conn.execute("UPDATE addresses SET sort_order=? WHERE phone=? AND id=?", (order_a, phone, addr_id))

    def delete_address(self, phone: str, addr_id: str):
        with _get_conn() as conn:
            conn.execute("DELETE FROM addresses WHERE phone=? AND id=?", (phone, addr_id))

    def get_orders(self, phone: str) -> list:
        with _get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM orders WHERE phone=? ORDER BY created_at ASC",
                (phone,)
            ).fetchall()
            return [dict(r) | {"is_booking": bool(r["is_booking"])} for r in rows]

    def add_order(self, phone: str, order: dict):
        with _get_conn() as conn:
            conn.execute(
                """INSERT INTO orders
                   (id, phone, drone_id, drone_name, start_address, start_location,
                    address, location, start_time, total_price, status, created_at, is_booking)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (order.get("id", ""), phone,
                 order.get("drone_id", ""), order.get("drone_name", ""),
                 order.get("start_address", ""), order.get("start_location", ""),
                 order.get("address", ""), order.get("location", ""),
                 order.get("start_time", ""), order.get("total_price", 0),
                 order.get("status", ""), order.get("created_at", ""),
                 1 if order.get("is_booking") else 0)
            )

    def get_order_by_id(self, phone: str, order_id: str) -> dict | None:
        with _get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM orders WHERE phone=? AND id=?", (phone, order_id)
            ).fetchone()
            if not row:
                return None
            return dict(row) | {"is_booking": bool(row["is_booking"])}

    def update_order_status(self, phone: str, order_id: str, status: str):
        with _get_conn() as conn:
            conn.execute(
                "UPDATE orders SET status=? WHERE phone=? AND id=?",
                (status, phone, order_id)
            )

    def cancel_order(self, phone: str, order_id: str):
        self.update_order_status(phone, order_id, "已取消")

    def contains(self, phone: str) -> bool:
        with _get_conn() as conn:
            row = conn.execute("SELECT 1 FROM users WHERE phone=?", (phone,)).fetchone()
            return row is not None

    def add(self, phone: str, nick_name: str, password: str):
        with _get_conn() as conn:
            conn.execute(
                "INSERT INTO users (phone, nick_name, password, gender, birthday) VALUES (?,?,?,?,?)",
                (phone, nick_name, self._hash_password(password), "保密", "")
            )

    def delete(self, phone: str):
        with _get_conn() as conn:
            conn.execute("DELETE FROM users WHERE phone=?", (phone,))

    def update_value(self, phone, nick_name, gender, birthday):
        with _get_conn() as conn:
            conn.execute(
                "UPDATE users SET nick_name=?, gender=?, birthday=? WHERE phone=?",
                (nick_name, gender, birthday, phone)
            )

    def update_password(self, phone, new_password):
        with _get_conn() as conn:
            conn.execute(
                "UPDATE users SET password=? WHERE phone=?",
                (self._hash_password(new_password), phone)
            )

    def update_key(self, phone_old, phone_new) -> bool:
        if self.contains(phone_new):
            return False
        with _get_conn() as conn:
            conn.execute("UPDATE users SET phone=? WHERE phone=?", (phone_new, phone_old))
            conn.execute("UPDATE addresses SET phone=? WHERE phone=?", (phone_new, phone_old))
            conn.execute("UPDATE orders SET phone=? WHERE phone=?", (phone_new, phone_old))
        return True

    def verify_login(self, phone: str, input_password: str) -> bool:
        with _get_conn() as conn:
            row = conn.execute("SELECT password FROM users WHERE phone=?", (phone,)).fetchone()
            if not row:
                return False
            return row["password"] == self._hash_password(input_password)

    def save(self):
        pass
