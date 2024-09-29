from __future__ import annotations

import os

from dotenv import load_dotenv

from src.server import app

load_dotenv()

PORT = os.getenv("PORT", 80)

if __name__ == "__main__":
    app.run(port=int(5000), threaded=True, host="0.0.0.0")
