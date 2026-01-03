from flask import abort, make_response
from flask import Flask, render_template
from task_tracker import TaskTracker

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "main":
    app.run(host="0.0.0.0", port=8000, debug=True)