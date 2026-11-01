import requests
from app import app

def test_home_page():
    r=app.test_client().get("/")
    assert r.status_code==200 and b"SkyCast" in r.data and b"search-form" in r.data

def test_health():
    r=app.test_client().get("/health")
    assert r.status_code==200 and r.get_json()=={"status":"ok"}

def test_city_required():
    r=app.test_client().get("/api/weather")
    assert r.status_code==400 and "error" in r.get_json()

def test_city_length_validation():
    assert app.test_client().get("/api/weather?city="+"a"*101).status_code==400

def test_unknown_city(monkeypatch):
    class FakeResponse:
        def raise_for_status(self): pass
        def json(self): return {"results":[]}
    monkeypatch.setattr("app.requests.get",lambda *a,**kw:FakeResponse())
    r=app.test_client().get("/api/weather?city=NotARealCity")
    assert r.status_code==404 and "No location found" in r.get_json()["error"]

def test_provider_timeout(monkeypatch):
    def fail(*a,**kw): raise requests.Timeout("timeout")
    monkeypatch.setattr("app.requests.get",fail)
    r=app.test_client().get("/api/weather?city=Hyderabad")
    assert r.status_code==502 and "temporarily unavailable" in r.get_json()["error"]
