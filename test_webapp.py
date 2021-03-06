import os

os.environ['SECRET_KEY'] = '1234'
os.environ['CAMPUS_NET_APP_NAME'] = '123'
os.environ['CAMPUS_NET_APP_TOKEN'] = '1234'
os.environ['CONFIG_FILE'] = 'app.cfg.example'

from webapp import (app, SessionAuthentication, UserCVBuilder)
from pytest import yield_fixture
from mock import Mock, MagicMock
from base64 import b64encode as base64
import webapp


class FakeCampusNetPicture(object):
    def iter_content(self, size):
        return ['user', '_picture']


class FakeCampusNetClient(object):
    def __init__(self):
        self.success = True
        self.auth_token = 'LSSJK-28SJS'

    def is_authenticated(self):
        return self.success

    def authenticate(self, username, password):
        pass

    def authenticate_with_token(self, student_id, auth_token):
        pass

    def user(self):
        return MagicMock(user_id=1234)

    def user_picture(self, user_id):
        return FakeCampusNetPicture()


class NullObject(object):
    def __call__(self):
        return NullObject()

    def __getattr__(self, name):
        return NullObject()

    def __iter__(self):
        return self

    def __next__(self):
        raise StopIteration

    def next(self):
        self.__next__()


@yield_fixture
def api():
    app.debug = True
    app.testing = True
    yield app.test_client()


@yield_fixture
def fake_cn_client(monkeypatch):
    cn_client = FakeCampusNetClient()
    monkeypatch.setattr(webapp, 'campus_net_client', cn_client)
    yield cn_client


def _auth_headers():
    basic_auth_creds = base64("usrname:secret".encode('ascii'))
    return {
        'Authorization': 'Basic %s' % basic_auth_creds.decode('ascii'),
        'Content-Type': 'application/json'
    }


def assert_redirected_to(response, path):
    assert response.status_code == 302
    assert response.location == "http://localhost%s" % path


def test_root_simply_render(api):
    respone = api.get('/')
    assert respone.status_code == 200


def test_authenticated_users_are_redirected_to_cv_in_root(api, monkeypatch):
    monkeypatch.setattr(SessionAuthentication, 'is_authenticated',
                        lambda self: True)
    response = api.get('/', follow_redirects=False)
    assert_redirected_to(response, '/cv')


def test_correct_authentications_responds_with_200(api, monkeypatch,
                                                   fake_cn_client):
    response = api.get('/auth', headers=_auth_headers())
    assert response.status_code == 200


def test_authentication_with_correct_credentials(api, monkeypatch):
    campus_net_client_mock = Mock(auth_token='LSSJK-28SJS')
    monkeypatch.setattr(webapp, 'campus_net_client', campus_net_client_mock)
    api.get('/auth', headers=_auth_headers())
    campus_net_client_mock.authenticate.assert_called_with('usrname',
                                                           'secret')


def test_correct_authentication_updates_session(api, monkeypatch,
                                                fake_cn_client):
    session_auth_mock = Mock(return_value=None)
    monkeypatch.setattr(SessionAuthentication, 'authenticate',
                        session_auth_mock)
    api.get('/auth', headers=_auth_headers())
    session_auth_mock.assert_called_with('usrname', 'LSSJK-28SJS')


def test_bad_authentication_responds_with_401(api, monkeypatch,
                                              fake_cn_client):
    fake_cn_client.success = False
    response = api.get('/auth', headers=_auth_headers())
    assert response.status_code == 401


def test_log_out_invokes_session_log_out(api, monkeypatch):
    session_auth_mock = Mock(return_value=None)
    monkeypatch.setattr(SessionAuthentication, 'log_out',
                        session_auth_mock)
    api.post('/log_out')
    session_auth_mock.assert_called_with()


def test_log_out_redirects_to_root(api, monkeypatch):
    monkeypatch.setattr(SessionAuthentication, 'log_out', lambda x: None)
    response = api.post('/log_out')
    assert_redirected_to(response, '/')


def test_cv_page_redirects_to_root_when_unauthenticated(api, monkeypatch,
                                                        fake_cn_client):
    monkeypatch.setattr(SessionAuthentication, 'is_authenticated',
                        lambda self: False)
    response = api.get('/cv')
    assert_redirected_to(response, '/')


def test_cv_page_renders_the_cv_for_authenticated_users(api, monkeypatch,
                                                        fake_cn_client):
    monkeypatch.setattr(SessionAuthentication, 'is_authenticated',
                        lambda self: True)
    monkeypatch.setattr(UserCVBuilder, 'build', lambda self: NullObject())
    response = api.get('/cv')
    assert response.status_code == 200


def test_picture_responds_with_401_when_uanauthenticate(api, monkeypatch,
                                                        fake_cn_client):
    fake_cn_client.success = False
    response = api.get('/cv/picture')
    assert response.status_code == 401


def test_picture_responds_with_image_when_authenticated(api, monkeypatch,
                                                        fake_cn_client):
    monkeypatch.setattr(SessionAuthentication, 'is_authenticated',
                        lambda self: True)
    response = api.get('/cv/picture')
    assert response.status_code == 200
    assert response.data == 'user_picture'.encode('ascii')
