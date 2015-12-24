import datetime

from kano.utils.shell import run_cmd

def get_date_now():
    return datetime.datetime.utcnow().isoformat()


def is_number(string):
    try:
        float(string)
        return True
    except (ValueError, TypeError):
        return False


def uniqify_list(seq):
    # Order preserving
    seen = set()
    return [x for x in seq if x not in seen and not seen.add(x)]


def is_installed(program):
    '''
    Returns True if "program" is recognized as an executable command in PATH
    '''
    _, _, rc = run_cmd('which {}'.format(program))
    return rc == 0
