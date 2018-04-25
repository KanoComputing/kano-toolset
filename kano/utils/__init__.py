# __init__.py
#
# Copyright (C) 2014-2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Init for the kano utils module


__author__ = 'Kano Computing Ltd.'
__email__ = 'dev@kano.me'

import sys

def ku_audio(name):
    import kano.utils.audio
    return getattr(kano.utils.audio, name)

def ku_file_operations(name):
    import kano.utils.file_operations
    return getattr(kano.utils.file_operations, name)

def ku_disk(name):
    import kano.utils.disk
    return getattr(kano.utils.disk, name)

def ku_gui(name):
    import kano.utils.gui
    return getattr(kano.utils.gui, name)

def ku_hardware(name):
    import kano.utils.hardware
    return getattr(kano.utils.hardware, name)

def ku_http_requests(name):
    import kano.utils.http_requests
    return getattr(kano.utils.http_requests, name)

def ku_misc(name):
    import kano.utils.misc
    return getattr(kano.utils.misc, name)

def ku_processes(name):
    import kano.utils.processes
    return getattr(kano.utils.processes, name)

def ku_shell(name):
    import kano.utils.shell
    return getattr(kano.utils.shell, name)

def ku_system(name):
    import kano.utils.system
    return getattr(kano.utils.system, name)

def ku_user(name):
    import kano.utils.user
    return getattr(kano.utils.user, name)
        
functable = {
    'play_sound': ku_audio,
    'percent_to_millibel': ku_audio,
    'get_volume': ku_audio,

    'read_file_contents': ku_file_operations,
    'write_file_contents': ku_file_operations,
    'read_file_contents_as_lines': ku_file_operations,
    'delete_dir': ku_file_operations,
    'delete_file': ku_file_operations,
    'ensure_dir': ku_file_operations,
    'list_dir': ku_file_operations,
    'chown_path': ku_file_operations,
    'read_json': ku_file_operations,
    'write_json': ku_file_operations,
    'open_locked': ku_file_operations,
    'sed': ku_file_operations,

    'get_free_space': ku_disk,
    'get_partition_info': ku_disk,

    'is_gui': ku_gui,
    'zenity_show_progress': ku_gui,

    'detect_kano_keyboard': ku_hardware,
    'is_model_a': ku_hardware,
    'is_model_b': ku_hardware,
    'is_model_b_plus': ku_hardware,
    'is_model_zero': ku_hardware,
    'is_model_2_b': ku_hardware,
    'get_rpi_model': ku_hardware,
    'is_monitor': ku_hardware,
    'get_mac_address': ku_hardware,
    'get_cpu_id': ku_hardware,
    'has_min_performance': ku_hardware,

    'RPI_A_SCORE': ku_hardware,
    'RPI_A_PLUS_SCORE': ku_hardware,
    'RPI_B_SCORE': ku_hardware,
    'RPI_B_PLUS_SCORE': ku_hardware,
    'RPI_ZERO_SCORE': ku_hardware,
    'RPI_COMPUTE_SCORE': ku_hardware,
    'RPI_2_B_SCORE': ku_hardware,

    'proxies': ku_http_requests,
    'download_url': ku_http_requests,
    'requests_get_json': ku_http_requests,
    'debug_requests': ku_http_requests,
    'get_date_now': ku_misc,
    'is_number': ku_misc,
    'uniqify_list': ku_misc,
    'is_installed': ku_misc,

    'kill_child_processes': ku_processes,
    'is_running': ku_processes,
    'get_program_name': ku_processes,
    'pkill': ku_processes,

    'run_cmd': ku_shell,
    'run_cmd_log': ku_shell,
    'run_bg': ku_shell,
    'run_term_on_error': ku_shell,
    'run_print_output_error': ku_shell,
    'restore_signals': ku_shell,

    'is_jessie': ku_system,
    'is_stretch': ku_system,
    'is_systemd': ku_system,


    'get_user_getpass': ku_user,
    'get_user': ku_user,
    'get_user_unsudoed': ku_user,
    'get_home': ku_user,
    'get_home_by_username': ku_user,
    'get_all_home_folders': ku_user,
    'enforce_root': ku_user

}

# lazy loader: only import utils module when actually used
class loader:
    def __init__(self, oldmodule):
        self.oldmodule = oldmodule

    def __getattr__(self, name):
        if name in functable:
            return functable[name](name)
        else:
            return getattr(self.oldmodule, name)


sys.modules[__name__] = loader(sys.modules[__name__])
