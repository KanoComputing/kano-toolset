# logging_bash.sh
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# bash logging functions compatible with kano.logging
# Usage:
#
# . /usr/share/kano-toolset/logging_bash.sh
#
# set_app_name "make-minecraft"
#
# log_timestamp "This is an interesting point to take note of"
#
# log_msg_to_json warning "tread carefully"

APP_NAME="$0"

logger_set_app_name()
{
    export APP_NAME="$1"
}

# Sample minimum log message example:
# "message": "Screen model: SyncMaster", "level": "info", "pid": 1832, "time": 1423047420.465359}

# We look for this file, only if it exists we log messages
profiling_conf_file="/etc/kano-profiling.conf"

#This function provides the means to append a message to the application log from bash
#The main purpose for this is to help profile the code
#Thus it doesn't call the python interpreter, but is more rudimentary
# It only takes one argument, the message that accompanies the timestamp in the log
function log_timestamp
{
    # ideally we want to check for the file only once per program execution.
    # once we find it, we set a variable
    if [ "$prof_log_en" == ""  ]; then
        if [ -e "$profiling_conf_file"  ]; then
            echo `date +%s.%06N`#$1
            prof_log_en="y"
        else
            prof_log_en="n"
        fi
    fi

    if [ "$prof_log_en" == "y"  ]; then
        log_msg_to_json debug $1
    fi
}

dot_slash="./"
log_msg_location="$HOME/.kano-logs/$APP_NAME.log"
log_msg_location="${log_msg_location/$dot_slash/}"

# Parameters for this function, with regard to position:
# 1: level, can be "error", "warning", "info", "debug", else it defaults to "none"
# 2: Message to be logged
function log_msg_to_json
{
    local level="$1"

    if [ "$level" != "error" ] && [ "$level" != "warning" ] &&
       [ "$level" != "info" ] && [ "$level" != "debug" ]; then
        level="none"
    fi

    local time="`date +%s.%06N`"

    local line='{"message": "%s", "level": "%s", "pid": %i, "time": %s}\n'

    printf "$line" "$2" "$level" $$ "$time" >> "$log_msg_location"
}

