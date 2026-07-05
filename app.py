import os

from app import app


if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "False") == "True"
    app.run(debug=debug, port=5002 , host="0.0.0.0")