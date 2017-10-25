#
# webapp.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Fixtures for the WebApp browser
#


import re
import pytest

WEB_URI_RE = re.compile(r'^https?://.+$')
SCHEME_URI_RE = re.compile(r'^kano:.+$')
API_URI_RE = re.compile(r'^.*#api:.+$')


SAMPLE_URIS = (
    'http://www.kano.me',
    'kano:share:123456789',
    'http://www.kano.me/something#api:some_func[12345]/args'
)


@pytest.fixture(scope='function')
def webapp(monkeypatch):
    '''
    Instance of the WebApp class adapted for use in tests
    '''

    import gtk
    from kano.webapp import WebApp

    app = WebApp()
    app._index = 'http://www.kano.me'

    monkeypatch.setattr(gtk, 'main', lambda *args: None)
    app.run()

    return app


@pytest.fixture(scope='function', params=SAMPLE_URIS)
def navigation_action(request):
    '''
    Navigation request objects mimicking those passed to the navigation request
    handler
    '''

    class FakeAction(object):
        def get_original_uri(self):
            return request.param

        def is_api_call(self):
            uri = self.get_original_uri()
            return bool(API_URI_RE.match(uri))

        def is_scheme_call(self):
            uri = self.get_original_uri()
            return not self.is_api_call() \
                and bool(SCHEME_URI_RE.match(uri))

        def is_web_call(self):
            uri = self.get_original_uri()
            return not self.is_api_call() \
                and not self.is_scheme_call() \
                and bool(WEB_URI_RE.match(uri))

    return FakeAction()
