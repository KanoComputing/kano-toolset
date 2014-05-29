# bash wrapper for kano.logger
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

CONF="/etc/debug"
APP_NAME="$0"

function _is_logger_enabled
{
    # The result is stored in a var, so this check
    # should happen just once per application runtime
    if [ -z "$LOGGER_ENABLED" ]; then
        if [ -e "$CONF" ]; then
            export LOGGER_ENABLED=1
        else
            export LOGGER_ENABLED=0
        fi
    fi
}

function logger_set_app_name
{
    export APP_NAME="$1"
}

function logger_write
{
    _is_logger_enabled

    if [ "$LOGGER_ENABLED" -eq 1 ]; then
        python <<EOF
import kano.logger as logger

# We already know that logging is enabled, so we force-enable it here.
# Therefore, python will not check the CONF file again.
logger.enable()

logger.pid = $$
logger.set_app_name("$APP_NAME")

logger.write("$1")
EOF
    fi
}
