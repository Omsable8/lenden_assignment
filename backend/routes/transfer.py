from flask import Blueprint, request, jsonify
from db import get_db

transfer_bp = Blueprint("transfer", __name__)

@transfer_bp.post("/transfer")
def transfer():
    data = request.get_json()
    sender = data.get("sender_id")
    receiver = data.get("receiver_id")
    amount = data.get("amount")

    if not sender or not receiver or not amount:
        return jsonify({"error": "Missing parameters"}), 400
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    try:
        # START TRANSACTION
        conn.start_transaction()

        # Validate sender balance
        cursor.execute("SELECT balance FROM users WHERE id=%s FOR UPDATE", (sender,))
        row = cursor.fetchone()
        if not row:
            raise Exception("Sender not found")

        if row["balance"] < amount:
            raise Exception("Insufficient funds")

        # Deduct from sender
        cursor.execute("UPDATE users SET balance = balance - %s WHERE id=%s", (amount, sender))

        # Credit to receiver
        cursor.execute("UPDATE users SET balance = balance + %s WHERE id=%s", (amount, receiver))

        # Insert into transactions table
        cursor.execute(
            "INSERT INTO transactions (sender_id, receiver_id, amount) VALUES (%s, %s, %s)",
            (sender, receiver, amount)
        )
        tx_id = cursor.lastrowid

        # COMMIT ATOMIC OPERATION
        conn.commit()

        # Asynchronous audit entry (you can use Celery later; for now just direct write)
        cursor.execute(
            "INSERT INTO audit_log (transaction_id, sender_id, receiver_id, amount, status) VALUES (%s,%s,%s,%s,%s)",
            (tx_id, sender, receiver, amount, "SUCCESS")
        )
        conn.commit()

        return jsonify({"message": "Transfer successful", "transaction_id": tx_id})

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400

    finally:
        cursor.close()
        conn.close()
