# logging.sh
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# bash wrapper for kano.logging
# Usage:
#
# . /usr/share/kano-toolset/logging.sh
#
# set_app_name "make-minecraft"
#
# logger_write "Error! Error!"

APP_NAME="$0"

logger_set_app_name()
{
    export APP_NAME="$1"
}

logger_write()
{
    __msg="$1"
    __level=$2

    __kwargs=""
    if [ -n "$__level" ]; then
        __kwargs="$__kwargs, level=\"$__level\""
    fi

    python <<EOF
from kano.logging import logger, normalise_level

logger._pid = $$
logger.set_app_name("$APP_NAME")
logger.write("""$__msg""" $__kwargs)
EOF
}

logger_error() { logger_write "$1" "error"; }
logger_info()  { logger_write "$1" "info"; }
logger_warn()  { logger_write "$1" "warning"; }
logger_debug() { logger_write "$1" "debug"; }

