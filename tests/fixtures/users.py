#
# users.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Fixtures for fake users
#


import os
import pwd
import pytest


TEST_USERS = [
    {
        'username': 'kanouser',
        'sudo': False
    },
    {
        'username': 'test123',
        'sudo': True
    },
    {
        'username': 'root',
        'sudo': False
    }
]

ENV_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), 'env'
)
USER_ENV = os.path.join(ENV_DIR, 'env_user')
SUDO_ENV = os.path.join(ENV_DIR, 'env_sudo')
ROOT_ENV = os.path.join(ENV_DIR, 'env_root')


@pytest.fixture(scope='function')
def load_env_conf(fs, monkeypatch):
    '''
    Provides a function to load an environment for a given user and patches the
    environment variables with these values.
    '''

    def load(username, sudo=False):
        if username == 'root':
            env_file = ROOT_ENV
        elif sudo:
            env_file = SUDO_ENV
        else:
            env_file = USER_ENV

        env = {}
        fs.add_real_file(env_file)

        with open(env_file) as env_f:
            for line in env_f.readlines():
                line = line.strip().rstrip()
                key, val = line.split('=', 1)
                val = val.replace('username', username)

                env[key] = val
                monkeypatch.setenv(key, val)

        return env

    return load


@pytest.fixture(scope='function')
def get_home_dir():
    '''
    Provides a function to get the home directory of a given user.
    '''

    def get_dir(username):
        if username == 'root':
            return os.path.join(os.path.sep, username)
        else:
            return os.path.join(os.path.sep, 'home', username)

    return get_dir



@pytest.fixture(scope='function')
def create_fake_user(fs, get_home_dir):
    '''
    Creates files for a fake user
    '''

    def create_user(username):
        fs.CreateDirectory(get_home_dir(username))

        return fs

    return create_user


@pytest.fixture(scope='function')
def fake_users(fs, get_home_dir, load_env_conf, create_fake_user, monkeypatch):
    '''
    Creates fake users and provides a function to fake logging into one of the
    accounts.
    '''

    def login(username, sudo=False):
        load_env_conf(username, sudo=sudo)

        uid = 0 if username == 'root' or sudo else 1001
        monkeypatch.setattr(
            os, 'getuid', lambda: uid
        )

        monkeypatch.setattr(
            os.path, 'expanduser',
            lambda path: path.replace('~', get_home_dir(username))
        )

        fs.patch = monkeypatch
        print 'patched'
        return monkeypatch

    users = []

    for user in TEST_USERS:
        fs = create_fake_user(user.get('username'))
        users.append(user.get('username'))


    fs.users = users
    fs.login = login
    fs.patch = monkeypatch

    return fs


@pytest.fixture(scope='function', params=TEST_USERS)
def fake_user(fake_users, request):
    '''
    Creates a series of users and provides a stream of logged in user profiles.
    '''

    user = request.param

    fake_users.username = user.get('username')
    fake_users.sudo = user.get('sudo')

    fake_users.patch = fake_users.login(
        fake_users.username, sudo=fake_users.sudo
    )

    return fake_users


@pytest.fixture(scope='function')
def fake_pwd(get_home_dir, monkeypatch):
    '''
    Mocks the `pwd` module to provide fake user information.
    '''

    class PwdStructPasswd(object):
        def __init__(self, username):
            self.pw_dir = get_home_dir(username)

    return monkeypatch.setattr(
        pwd, 'getpwnam',
        lambda username: PwdStructPasswd(username)
    )
