from app import app

def test_health():
    assert app.test_client().get("/health").status_code == 200

def test_home():
    assert b"SecScan" in app.test_client().get("/").data

from app import is_safe

def test_blocks_internal_addresses():
    assert not is_safe("http://127.0.0.1")
    assert not is_safe("http://localhost:5000")
    assert not is_safe("http://169.254.169.254/latest/meta-data")
    assert not is_safe("http://example.com:22")
