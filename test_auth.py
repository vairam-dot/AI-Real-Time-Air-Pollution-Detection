import pytest
from app import create_app
from app.config import Config


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def login(client, username, password):
    return client.post('/login', data={'username': username, 'password': password}, follow_redirects=True)


def logout(client):
    return client.get('/logout', follow_redirects=True)


def test_login_page_accessible(client):
    res = client.get('/login')
    assert res.status_code == 200
    assert b"Sign in" in res.data


def test_valid_login_redirects_dashboard(client):
    res = login(client, Config.ADMIN_USER, Config.ADMIN_PASS)
    # either we see the dashboard content or path changed
    assert res.status_code == 200
    assert b"Dashboard" in res.data


def test_invalid_login_shows_error(client):
    res = login(client, "wrong", "credentials")
    assert b"Invalid username or password" in res.data


def test_logout_clears_session(client):
    login(client, Config.ADMIN_USER, Config.ADMIN_PASS)
    res = logout(client)
    assert b"You have been logged out" in res.data
    res2 = client.get('/dashboard')
    assert res2.status_code == 302
    assert '/login' in res2.headers['Location']
