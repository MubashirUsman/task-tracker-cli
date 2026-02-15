from flask import Flask, render_template
from config import Config
from models import db
from routes import api
from logging_config import setup_logging
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
app.config.from_object(Config)

# Setup logging
logger = setup_logging(app)

metrics = PrometheusMetrics(app)

# Initialize SQLAlchemy
db.init_app(app)

# Register API blueprint
app.register_blueprint(api)


@app.route("/")
def home():
    return render_template("index.html")


# Create database tables
with app.app_context():
    db.create_all()
    logger.info("Database initialized")


if __name__ == "__main__":
    logger.info("Starting Task Tracker API server on port 8000")
    app.run(host="0.0.0.0", port=8000, debug=True)