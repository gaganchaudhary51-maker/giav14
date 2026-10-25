from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.desktop.static import mount_desktop_frontend


def test_desktop_frontend_serves_spa_assets_and_keeps_api_routes(tmp_path):
    (tmp_path / "index.html").write_text("<title>GIA desktop</title>", encoding="utf-8")
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets" / "app.js").write_text("window.gia = true", encoding="utf-8")
    app = FastAPI()
    app.get("/api/health")(lambda: {"status": "healthy"})

    assert mount_desktop_frontend(app, str(tmp_path)) is True
    client = TestClient(app)
    assert "GIA desktop" in client.get("/").text
    assert client.get("/assets/app.js").text == "window.gia = true"
    assert "GIA desktop" in client.get("/studio").text
    assert client.get("/api/health").json() == {"status": "healthy"}
    assert client.get("/api/unknown").status_code == 404
    assert client.get("/../secret.txt").status_code in {400, 404}


def test_desktop_frontend_is_not_mounted_without_a_built_index(tmp_path):
    app = FastAPI()
    assert mount_desktop_frontend(app, str(tmp_path)) is False
