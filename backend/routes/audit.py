from flask import Blueprint, jsonify
from db import get_db

audit_bp = Blueprint("audit", __name__)

@audit_bp.get("/history/<int:user_id>")
def history(user_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM audit_log
        WHERE sender_id = %s OR receiver_id = %s
        ORDER BY created_at DESC
    """, (user_id, user_id))

    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(rows)


# NEW ENDPOINT: Fetch user balance
@audit_bp.get("/balance/<int:user_id>")
def get_balance(user_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT balance FROM users WHERE id=%s", (user_id,))
    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if not row:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"balance": row["balance"]})
