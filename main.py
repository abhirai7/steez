from __future__ import annotations

import os

from dotenv import load_dotenv

from src.server import app

load_dotenv()

PORT = int(os.getenv("PORT", 80))

if __name__ == "__main__":
    app.run(port=PORT, threaded=True, host="0.0.0.0")
