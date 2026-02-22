from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from models import db, User
from routes import api
from logging_config import setup_logging
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
app.config.from_object(Config)

logger = setup_logging(app)
metrics = PrometheusMetrics(app)

db.init_app(app)
app.register_blueprint(api)


@app.route("/")
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template("index.html", username=session.get('username'))


@app.route("/login", methods=["GET", "POST"])
def login():
    if 'user_id' in session:
        return redirect(url_for('home'))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username and password are required.", "error")
            return render_template("login.html")

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            logger.info(f"User '{username}' logged in")
            return redirect(url_for('home'))

        flash("Invalid username or password.", "error")
        return render_template("login.html")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if 'user_id' in session:
        return redirect(url_for('home'))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not username or not password:
            flash("Username and password are required.", "error")
            return render_template("register.html")

        if len(password) < 4:
            flash("Password must be at least 4 characters.", "error")
            return render_template("register.html")

        if password != confirm:
            flash("Passwords do not match.", "error")
            return render_template("register.html")

        if User.query.filter_by(username=username).first():
            flash("Username already taken.", "error")
            return render_template("register.html")

        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        logger.info(f"New user registered: '{username}'")
        flash("Account created! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template("register.html")


@app.route("/logout")
def logout():
    username = session.get('username', 'unknown')
    session.clear()
    logger.info(f"User '{username}' logged out")
    return redirect(url_for('login'))


with app.app_context():
    db.create_all()
    logger.info("Database initialized")


if __name__ == "__main__":
    logger.info("Starting Task Tracker API server on port 8000")
    app.run(host="0.0.0.0", port=8000, debug=False)