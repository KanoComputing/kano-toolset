# http_requests.py
#
# Copyright (C) 2014-2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Utilities relating to http requests


try:
    from kano_settings.system.proxy import get_requests_proxies
    proxies = get_requests_proxies()
except Exception:
    proxies = None


def download_url(url, file_path):
    import requests
    try:
        with open(file_path, 'wb') as handle:
            request = requests.get(url, stream=True, proxies=proxies)
            if not request.ok:
                return False, request.text
            for block in request.iter_content(1024):
                if not block:
                    break
                handle.write(block)
        return True, None
    except Exception as e:
        return False, str(e)


def requests_get_json(url, params=None):
    import requests
    try:
        r = requests.get(url, params=params, proxies=proxies)
        if r.ok:
            return r.ok, None, r.json()
        else:
            return r.ok, r.text, None
    except Exception as e:
        return False, str(e), None


def debug_requests():
    import httplib

    old_send = httplib.HTTPConnection.send

    def new_send(self, data):
        print data
        return old_send(self, data)
    httplib.HTTPConnection.send = new_send
