"""PyInstaller entry point for the GIA desktop backend sidecar."""
import os

import uvicorn

from app.main import app


def main():
    port = int(os.environ.get("GIA_DESKTOP_PORT", "8765"))
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning", access_log=False)


if __name__ == "__main__":
    main()
