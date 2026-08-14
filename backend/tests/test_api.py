from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)
def test_health():
 r=client.get('/api/health'); assert r.status_code==200; assert r.json()['status']=='healthy'
def test_create_project():
 auth=client.post('/api/auth/signup',json={'email':'legacy_api@example.com','password':'StrongPass123!','name':'Legacy'}).json()['token']; r=client.post('/api/projects',headers={'Authorization':f'Bearer {auth}'},json={'name':'CRM'}); assert r.status_code==201; assert r.json()['name']=='CRM'
