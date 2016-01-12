import os
import sys
import signal
import subprocess

def restore_signals():
    signals = ('SIGPIPE', 'SIGXFZ', 'SIGXFSZ')
    for sig in signals:
        if hasattr(signal, sig):
            signal.signal(getattr(signal, sig), signal.SIG_DFL)


def run_cmd(cmd, localised=False, unsudo=False):
    '''
    Executes cmd, returning stdout, stderr, return code
    if localised is False, LC_ALL will be set to "C"
    '''
    env = os.environ.copy()
    if not localised:
        env['LC_ALL'] = 'C'

    if unsudo and \
            'SUDO_USER' in os.environ and \
            os.environ['SUDO_USER'] != 'root':
        cmd = "sudo -u {} bash -c '{}' ".format(os.environ['SUDO_USER'], cmd)

    process = subprocess.Popen(cmd, shell=True, env=env,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               preexec_fn=restore_signals)

    stdout, stderr = process.communicate()
    returncode = process.returncode
    return stdout, stderr, returncode


def run_cmd_log(cmd, localised=False, unsudo=False):
    '''
    Wrapper against run_cmd but Kano Logging executuion and return code
    '''

    from kano.logging import logger

    out, err, rv = run_cmd(cmd, localised, unsudo)
    logger.info("Command: {}".format(cmd))

    if len(out.strip()) > 0:
        logger.info(out)

    if len(err.strip()) > 0:
        logger.error(err)

    logger.info("Return value: {}".format(rv))

    return out, err, rv


def run_bg(cmd, localised=False, unsudo=False):
    '''
    Starts cmd program in the background
    '''
    env = os.environ.copy()
    if not localised:
        env['LC_ALL'] = 'C'

    if unsudo and \
            'SUDO_USER' in os.environ and \
            os.environ['SUDO_USER'] != 'root':
        cmd = "sudo -u {} bash -c '{}' ".format(os.environ['SUDO_USER'], cmd)

    s = subprocess.Popen(cmd, shell=True, env=env)
    return s


def run_term_on_error(cmd, localised=False):
    o, e, rc = run_cmd(cmd, localised)
    if e:
        sys.exit(
            '\nCommand:\n{}\n\nterminated with error:\n{}'
            .format(cmd, e.strip())
        )
    return o, e, rc


def run_print_output_error(cmd, localised=False):
    o, e, rc = run_cmd(cmd, localised)
    if o or e:
        print '\ncommand: {}'.format(cmd)
    if o:
        print 'output:\n{}'.format(o.strip())
    if e:
        print '\nerror:\n{}'.format(e.strip())
    return o, e, rc
