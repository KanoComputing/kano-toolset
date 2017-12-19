#
# test_webapp.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Tests for the WebApp browser
#


import os
import pytest


@pytest.mark.gtk
def test_navigation_requests(monkeypatch, webapp, navigation_action):
    '''
    Ensures that custom navigation requests to the webapp are parsed correctly.

    Does this by replacing the functions that would be called for the navigation
    and ensuring that the correct function is called with the correct arguments
    '''

    assert navigation_action.is_api_call() \
        or navigation_action.is_scheme_call() \
        or navigation_action.is_web_call(), \
        'The sample request is not valid'

    uri = navigation_action.get_original_uri()

    func_called = {
        'fake_os_system': False,
        'fake_func': False
    }

    if navigation_action.is_api_call():
        '''
        The API receives a function name and arguments which it is supposed to
        call. Create a fake function to be called to ensure that this is working
        correctly.
        '''

        data = webapp._parse_api_call(uri)
        func = data[0]
        call_args = ()
        if len(data) >= 3:
            call_args = data[2]

        def fake_func(*args, **kwargs):
            '''
            Stub function to ensure that the API call does the right thing
            '''

            func_called['fake_func'] = True

            if not navigation_action.is_api_call():
                assert False, 'Function should only be called for API URIs'

            assert args == call_args, 'API function call arguments incorrect'

        monkeypatch.setattr(webapp, func, fake_func, raising=False)


    def fake_os_system(*args, **kwargs):
        '''
        Stub function to ensure that the scheme calls do the right thing
        '''
        func_called['fake_os_system'] = True

        if not navigation_action.is_scheme_call():
            assert False, 'Funciton should only be called for scheme URIs'

        assert \
            args[0] == 'systemd-run --user /usr/bin/xdg-open {}'.format(uri), \
            'Scheme launch command is incorrect'


    monkeypatch.setattr(os, 'system', fake_os_system)
    webapp._nav_req_handler(
        view=webapp._view,
        frame=None,
        request=None,
        action=navigation_action,
        decision=None,
        data=None
    )

    assert \
        func_called['fake_os_system'] == navigation_action.is_scheme_call(), \
        'Scheme handling function did not run when it should have'
    assert func_called['fake_func'] == navigation_action.is_api_call(), \
        'API handling function did not run when it should have'
