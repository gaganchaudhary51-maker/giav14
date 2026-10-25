from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse


def mount_desktop_frontend(app: FastAPI, frontend_dir: str) -> bool:
    """Serve the bundled SPA on the local API origin when a desktop build is configured."""
    if not frontend_dir:
        return False
    root = Path(frontend_dir).resolve()
    index = root / "index.html"
    if not index.is_file():
        return False

    def serve_index():
        return FileResponse(index)

    def serve_asset_or_route(asset_path: str):
        if asset_path == "api" or asset_path.startswith("api/"):
            raise HTTPException(404, "API route not found")
        candidate = (root / asset_path).resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            raise HTTPException(404, "Asset not found") from None
        if candidate.is_file():
            return FileResponse(candidate)
        if Path(asset_path).suffix:
            raise HTTPException(404, "Asset not found")
        return FileResponse(index)

    app.add_api_route("/", serve_index, methods=["GET"], include_in_schema=False)
    app.add_api_route("/{asset_path:path}", serve_asset_or_route,
                      methods=["GET"], include_in_schema=False)
    return True
