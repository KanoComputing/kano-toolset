#!/usr/bin/env python

# __init__.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

__author__ = 'Kano Computing Ltd.'
__email__ = 'dev@kano.me'


from kano.utils.file_operations import \
    read_file_contents, write_file_contents, read_file_contents_as_lines, \
    delete_dir, delete_file, ensure_dir, list_dir, chown_path, read_json, \
    write_json, open_locked, sed
from kano.utils.user import \
    get_user_getpass, get_user, get_user_unsudoed, get_home, \
    get_home_by_username, get_all_home_folders, enforce_root
from kano.utils.audio import \
    play_sound, percent_to_millibel, get_volume
from kano.utils.hardware import \
    detect_kano_keyboard, is_model_a, is_model_b, is_model_b_plus, \
    is_model_2_b, get_rpi_model, is_monitor, get_mac_address, get_cpu_id
from kano.utils.processes import \
    kill_child_processes, is_running, get_program_name, pkill
from kano.utils.gui import \
    is_gui, zenity_show_progress
from kano.utils.shell import \
    run_cmd, run_cmd_log, run_bg, run_term_on_error, run_print_output_error, \
    restore_signals
from kano.utils.http_requests import \
    proxies, download_url, requests_get_json, debug_requests
from kano.utils.disk import \
    get_free_space, get_partition_info
from kano.utils.misc import \
    get_date_now, is_number, uniqify_list, is_installed
from kano.utils.system import \
    is_jessie, is_systemd
