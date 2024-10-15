from __future__ import annotations

import asyncio
import os

import uvicorn
from asgiref.wsgi import WsgiToAsgi
from dotenv import load_dotenv

from src.server import app

if os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
else:
    try:
        import uvloop

        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except ImportError:
        pass

load_dotenv()

PORT = int(os.getenv("PORT", 80))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
HOST = os.getenv("HOST", "0.0.0.0")


asgi_app = WsgiToAsgi(app)

if __name__ == "__main__":
    if DEBUG:
        app.run(host=HOST, port=PORT, debug=True)
    else:
        uvicorn.run(asgi_app, host=HOST, port=PORT, log_level="debug", lifespan="off")
