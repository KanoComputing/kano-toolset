#
# test_user.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Tests for the kano.utils.user module
#


def test_get_user_pass():
    pass


def test_get_user(fake_user):
    from kano.utils.user import get_user

    user = get_user()

    if fake_user.sudo:
        assert user == 'root'
    else:
        assert user == fake_user.username


def test_get_user_unsudoed(fake_user):
    from kano.utils.user import get_user_unsudoed

    assert get_user_unsudoed() == fake_user.username


def test_get_home(fake_user, get_home_dir):
    from kano.utils.user import get_home

    assert get_home() == get_home_dir(fake_user.username)


def test_get_home_by_username(fake_users, fake_pwd, get_home_dir):
    from kano.utils.user import get_home_by_username

    for user in fake_users.users:
        assert get_home_by_username(user) == get_home_dir(user)


def test_get_all_home_folders(fake_users, get_home_dir):
    from kano.utils.user import get_all_home_folders
    home_dirs = get_all_home_folders()
    assert set(home_dirs) == set([
        get_home_dir(username) for username in fake_users.users
        if username != 'root'
    ])


def test_get_all_home_folders_with_root(fake_users, get_home_dir):
    from kano.utils.user import get_all_home_folders
    home_dirs = get_all_home_folders(root=True)
    assert set(home_dirs) == set([
        get_home_dir(username) for username in fake_users.users
    ])


def test_get_all_home_folders_with_skel(fake_users, get_home_dir):
    from kano.utils.user import get_all_home_folders
    home_dirs = get_all_home_folders(skel=True)
    assert set(home_dirs) == set([
        get_home_dir(username) for username in fake_users.users
        if username != 'root'
    ] + ['/etc/skel'])


def test_get_all_home_folders_with_root_skel(fake_users, get_home_dir):
    from kano.utils.user import get_all_home_folders
    home_dirs = get_all_home_folders(root=True, skel=True)
    assert set(home_dirs) == set([
        get_home_dir(username) for username in fake_users.users
    ] + ['/etc/skel'])


def test_enforce_root(fake_user, fake_sys_exit):
    from kano.utils.user import enforce_root
    enforce_root('Must be root')

    expect_quit = fake_user.username != 'root' and not fake_user.sudo
    assert fake_sys_exit.quit == expect_quit
