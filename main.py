from src.server import app

if __name__ == "__main__":
    app.run(debug=True, port=5000, threaded=True)
