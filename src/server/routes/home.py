from src.server import app


@app.route("/")
def home():
    return "Hello, World!"
