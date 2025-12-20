from flask import Blueprint, request, jsonify
from db import get_db

audit_bp = Blueprint("audit", __name__)

@audit_bp.get("/history/<int:user_id>")
def history(user_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM audit_log
        WHERE sender_id=%s OR receiver_id=%s
        ORDER BY created_at DESC
    """, (user_id, user_id))

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(rows)
