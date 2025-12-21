from flask import Blueprint, request, jsonify
from db import get_db
from routes.socket_manager import socketio

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
        conn.start_transaction()

        cursor.execute("SELECT balance FROM users WHERE id=%s FOR UPDATE", (sender,))
        row = cursor.fetchone()

        if not row:
            raise Exception("Sender not found")
        if row["balance"] < amount:
            raise Exception("Insufficient funds")

        cursor.execute(
            "UPDATE users SET balance = balance - %s WHERE id=%s", 
            (amount, sender)
        )
        cursor.execute(
            "UPDATE users SET balance = balance + %s WHERE id=%s", 
            (amount, receiver)
        )

        cursor.execute("""
            INSERT INTO transactions (sender_id, receiver_id, amount)
            VALUES (%s, %s, %s)
        """, (sender, receiver, amount))
        tx_id = cursor.lastrowid

        conn.commit()

        # Insert into Audit Log
        cursor.execute("""
            INSERT INTO audit_log (transaction_id, sender_id, receiver_id, amount, status)
            VALUES (%s, %s, %s, %s, %s)
        """, (tx_id, sender, receiver, amount, "SUCCESS"))
        conn.commit()

        # Fetch updated balances
        cursor.execute("SELECT balance FROM users WHERE id=%s", (sender,))
        new_sender_balance = float(cursor.fetchone()["balance"])

        cursor.execute("SELECT balance FROM users WHERE id=%s", (receiver,))
        new_receiver_balance = float(cursor.fetchone()["balance"])

        # Emit events to all connected clients
        socketio.emit("balance_update", {
            "user_id": sender,
            "balance": new_sender_balance,
        })

        socketio.emit("balance_update", {
            "user_id": receiver,
            "balance": new_receiver_balance,
        })

        socketio.emit("new_transaction", {
            "transaction_id": tx_id,
            "sender_id": sender,
            "receiver_id": receiver,
            "amount": amount,
        })

        return jsonify({
            "message": "Transfer successful",
            "transaction_id": tx_id
        })

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400

    finally:
        cursor.close()
        conn.close()
