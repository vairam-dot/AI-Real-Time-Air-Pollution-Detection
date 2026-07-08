from app import create_app
from app.config import Config

app = create_app()
app.config['TESTING'] = True
with app.test_client() as c:
    print('GET /login', c.get('/login').status_code)
    r2 = c.post('/login', data={'username': Config.ADMIN_USER, 'password': Config.ADMIN_PASS}, follow_redirects=True)
    print('POST /login path', r2.request.path)
    r3 = c.get('/dashboard')
    print('/dashboard after login', r3.status_code)
    c.get('/logout')
    r4 = c.get('/dashboard')
    print('/dashboard after logout', r4.status_code, r4.location)
