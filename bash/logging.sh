# bash wrapper for kano.logging
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Usage:
#
# . /usr/share/kano-toolset/logger.sh
#
# set_app_name "make-minecraft"
#
# logger_write "Error! Error!"

APP_NAME="$0"

function logger_set_app_name
{
    export APP_NAME="$1"
}

function logger_write
{
    local msg="$1"
    local level=$2

    local kwargs=""
    if [ -n "$level" ]; then
        kwargs="$kwargs, level=\"$level\""
    fi

    if [ -z "$LOG_LEVEL" ]; then
        export LOG_LEVEL="`kano-logs -l`"
    fi

    if [ -z "$DEBUG_LEVEL" ]; then
        export DEBUG_LEVEL="`kano-logs -d`"
    fi

    # Optimisation: Don't launch python unless logging is enabled
    if [ "$LOG_LEVEL" != "none" ] || [ "$DEBUG_LEVEL" != "none" ]; then
        python <<EOF
from kano.logging import logger, normalise_level

logger._pid = $$
logger._cached_log_level = normalise_level("$LOG_LEVEL")
logger._cached_debug_level = normalise_level("$DEBUG_LEVEL")

logger.set_app_name("$APP_NAME")

logger.write("""$msg""" $kwargs)
EOF
    fi
}

function logger_error { logger_write "$1" "error"; }
function logger_info  { logger_write "$1" "info"; }
function logger_warn  { logger_write "$1" "warning"; }
function logger_debug { logger_write "$1" "debug"; }

function logger_force_log_level { export LOG_LEVEL="$1"; }
function logger_force_debug_level { export DEBUG_LEVEL="$1"; }
