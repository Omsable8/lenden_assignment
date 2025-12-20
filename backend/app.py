from flask import Flask
from routes.transfer import transfer_bp
from routes.audit import audit_bp

app = Flask(__name__)

app.register_blueprint(transfer_bp)
app.register_blueprint(audit_bp)

if __name__ == "__main__":
    app.run(debug=True)
