from app.audit.log import AuditLog


def test_default_audit_log_uses_configured_data_directory(monkeypatch, tmp_path):
    monkeypatch.delenv("GIA_AUDIT_LOG", raising=False)
    monkeypatch.setenv("GIA_DATA_DIR", str(tmp_path))
    log = AuditLog()
    assert log.path == tmp_path / "audit" / "audit.jsonl"
    record = log.append("DEPENDENCY_CHECK", "test", {"ok": True})
    assert record["previous_hash"] == "GENESIS"
    assert log.path.is_file()


def test_explicit_audit_log_location_is_preserved(monkeypatch, tmp_path):
    target = tmp_path / "custom" / "events.jsonl"
    monkeypatch.setenv("GIA_AUDIT_LOG", str(target))
    assert AuditLog().path == target
