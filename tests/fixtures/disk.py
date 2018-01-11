#
# disk.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Fixtures for fake disk utils
#


import imp
import pytest


DF_OUTPUT = '''
Filesystem     1K-blocks    Used Available Use% Mounted on
/dev/root        7399352 4011436   3021788  58% /
'''.lstrip()
DF_FREE_MB = 2950


LSBLK_OUTPUT = '''
7948206080
 100663808
7834959872
'''.lstrip()
LSBLK_PARTITION_INFO = [
    7948206080,
    100663808,
    7834959872,
]


@pytest.fixture(scope='function')
def df(monkeypatch):
    '''
    Mocks the output from `df`.

    Note: This fixture auto-reimports the `kano.utils.disk` module, which we
          expect to be the one which requires the patch, however depending on
          the module, it may be required to re-import the module being tested
          as this fixture patches `kano.utils.run_cmd` and if the tested module
          depends on this directly and has already been loaded then the updated
          version will not propagate. To re-import use:

              import imp
              import module.to.be.tested
              imp.reload(module.to.be.tested)

    '''

    import kano.utils.shell

    def mock_run_cmd(cmd):
        if cmd.startswith('df'):
            return DF_OUTPUT, '', 0
        else:
            raise NotImplementedError(
                'Command run is not df: {}'.format(cmd)
            )

    patch = monkeypatch.setattr(kano.utils.shell, 'run_cmd', mock_run_cmd)
    import kano.utils.disk
    imp.reload(kano.utils.disk)
    return patch



@pytest.fixture(scope='function')
def lsblk(monkeypatch):
    '''
    Mocks the output from `lsblk`.

    Note: This fixture auto-reimports the `kano.utils.disk` module, which we
          expect to be the one which requires the patch, however depending on
          the module, it may be required to re-import the module being tested
          as this fixture patches `kano.utils.run_cmd` and if the tested module
          depends on this directly and has already been loaded then the updated
          version will not propagate. To re-import use:

              import imp
              import module.to.be.tested
              imp.reload(module.to.be.tested)

    '''

    import kano.utils.shell

    def mock_run_cmd(cmd):
        if cmd.startswith('lsblk'):
            return LSBLK_OUTPUT, '', 0
        else:
            raise NotImplementedError(
                'Command run is not lsblk: {}'.format(cmd)
            )

    patch = monkeypatch.setattr(kano.utils.shell, 'run_cmd', mock_run_cmd)
    import kano.utils.disk
    imp.reload(kano.utils.disk)

    return patch
