#
# keyboard.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Fixtures for fake keyboards
#


import imp
import os
import pytest


KEYBOARD_LSUSB_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), 'keyboard'
)
KEYBOARD_LSUSB_OUTPUTS = [
    ('no_keyboard', None),
    ('other_keyboard', None),
    ('en_keyboard', 'en'),
    ('es_keyboard', 'es'),
]



@pytest.fixture(scope='function', params=KEYBOARD_LSUSB_OUTPUTS)
def keyboard(request, fs, monkeypatch):
    '''
    Simulates different keyboards, mainly by their outputs from terminal
    commands.

    Note: This fixture auto-reimports the `kano.utils.hardware` module, which we
          expect to be the one which requires the patch, however depending on
          the module, it may be required to re-import the module being tested
          as this fixture patches `kano.utils.run_cmd` and if the tested module
          depends on this directly and has already been loaded then the updated
          version will not propagate. To re-import use:

              import imp
              import module.to.be.tested
              imp.reload(module.to.be.tested)

    '''

    kb_file, version = request.param

    lsusb_output_path = os.path.join(
        KEYBOARD_LSUSB_DIR,
        '{}.dump'.format(kb_file)
    )
    fs.add_real_file(lsusb_output_path)
    with open(lsusb_output_path, 'r') as lsusb_output_f:
        lsusb_output = lsusb_output_f.read()

    def fake_lsusb_out(cmd):
        if cmd.startswith('lsusb'):
            return lsusb_output, None, None
        else:
            raise NotImplementedError(
                'Command run is not lsusb: {}'.format(cmd)
            )

    import kano.utils.shell
    monkeypatch.setattr(kano.utils.shell, 'run_cmd', fake_lsusb_out)
    imp.reload(kano.utils.hardware)

    return version
