from flask import Flask
from routes.main import main_bp
from routes.upload import upload_bp
from routes.dashboard import dashboard_bp

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Blueprints registration
app.register_blueprint(main_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(dashboard_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
