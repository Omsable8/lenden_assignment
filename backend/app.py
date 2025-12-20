from flask import Flask
from flask_cors import CORS
from routes.transfer import transfer_bp
from routes.audit import audit_bp
from routes.socket_manager import socketio

app = Flask(__name__)
CORS(app)

app.register_blueprint(transfer_bp)
app.register_blueprint(audit_bp)

if __name__ == "__main__":
    socketio.init_app(app, cors_allowed_origins="*")
    socketio.run(app, debug=True)
