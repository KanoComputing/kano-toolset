#!/bin/bash
# logging.sh
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# bash logging functions compatible with kano.logging
# Usage:
#
# . /usr/share/kano-toolset/logging.sh
#
# log_timestamp "This is an interesting point to take note of"
# logger_warn "tread carefully"

APP_NAME="`basename $0`"


# Takes and exports the variables from the logging conf file
# it expects that in this file there will be the following:
# log_level:_value_
# output_level:_value_
function set_log_envs
{
    local kano_conf_file="/etc/kano-logs.conf"
    eval `awk '{print "export "toupper(substr($1, 0, length($1)))"=" "\""$2"\""}' "$kano_conf_file"`
}


set_log_envs


logger_set_app_name()
{
    export APP_NAME="$1"
}

# Sample minimum log message example:
# "message": "Screen model: SyncMaster", "level": "info", "pid": 1832, "time": 1423047420.465359}

# We look for this file, only if it exists we log timestamps
profiling_conf_file="/etc/kano-profiling.conf"

# logging_levels
# Please keep them in ascending order of severity
logging_lvls=("none"
              "debug"
              "info"
              "warning"
              "error")

# Returns the level to lowercase and checks whether it has an acceptable value
# i.e. is within the list logging_lvls (see above)
# If the input parameter is acceptable the return code is 0 otherwise 1
# To get the normalised String use in the following way (note the backticks):
#
# a=`normalise_log_lvl $var`

# Parameters:
# 1: level string, ex. "debug"
#
# WARNING: Contains a conversion to lowercase semantic that requires
#          bash V 4.0 and above
function normalise_log_lvl
{
    local level=$1
    local not_in_list=1

    #Convert to lowercase, only works with bash ver >= 4.0
    if [ "${BASH_VERSINFO[0]}" -ge 4 ]; then
        level=${level,,}
    fi

    for i in "${logging_lvls[@]}"; do
        if [ "$level" == "$i"  ]; then
            not_in_list=0
            break
        fi
    done

    if [ "$not_in_list" -eq 1 ]; then
        level="none"
    fi

    echo "$level"
    return $not_in_list
}

# Echoes the full path for the logfile
# If the user is root (i.e. EUID is 0) the log is stored in /var/
# otherwise it is stored in the user's home dir
# Usage:
# dir="`log_file_full_path my_log.log`"
function log_file_full_path
{
    SYSTEM_LOGS_DIR="/var/log/kano/"
    USER_LOGS_DIR="$HOME/.kano-logs/"

    if [ "$EUID" -eq 0 ]; then
        echo "$SYSTEM_LOGS_DIR$1"
    else
        echo "$USER_LOGS_DIR$1"
    fi

    return 0
}

# This returns whether the level given has higher priority than
# a baseline (should also be given), according to the order of the
# list logging_lvls.
# Return value: 0 if given lvl is more severe
#               1 if givel lvl is not significant enough
# Parameters:
# 1: level allowed
# 2: level we need to check
#
#Usage:
# cmp_log_level "$LOG_LEVEL" "$level"
function cmp_log_level
{
    local min_lvl_allowed="$1"
    local this_lvl="$2"
    local ret=0

    # TODO Handle the case when $1 == ""

    for i in "${logging_lvls[@]}"; do

        if [ "$min_lvl_allowed" == "$i" ]; then
            break
        fi

        if [ "$this_lvl" == "$i" ]; then
            ret=1
        fi
    done

    return "$ret"
}

#This function provides the means to append a message to the application log from bash
#The main purpose for this is to help profile the code
#Thus it doesn't call the python interpreter, but is more rudimentary
# It only takes one argument, the message that accompanies the timestamp in the log
# NOTE: please make sure that you have set the APP_NAME variable using logger_set_app_name
function logger_log_timestamp
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
        logger_log_msg debug "$1"
    fi
}

# Parameters for this function, with regard to position:
# 1: level, can be "error", "warning", "info", "debug",  not case sensitive
#    else it defaults to "none"
# 2: Message to be logged
function logger_log_msg
{
    local level="`normalise_log_lvl $1`"
    local log_msg_location="`log_file_full_path "$APP_NAME.log"`"
    local time="`date +%s.%06N`"
    local line_json='{"message": "%s", "level": "%s", "pid": %i, "time": %s}\n'
    local line_cmd='%s [%i] %s %s\n'
    local ret=1

    # Check whether we need to add to file
    cmp_log_level "`normalise_log_lvl "$LOG_LEVEL"`" "$level"
    local log_lvl="$?"

    # Check whether we need to echo to stderr
    cmp_log_level "`normalise_log_lvl "$OUTPUT_LEVEL"`" "$level"
    local output_lvl="$?"

    if [ "$log_lvl" -eq 0 ]; then
        printf "$line_json" "$2" "$level" $$ "$time" >> "$log_msg_location"
        ret=0
    fi

    if [ "$output_lvl" -eq 0 ]; then
        >&2 printf "$line_cmd" "$APP_NAME" $$ "$level" "$2"
        ret=0
    fi
    return "$ret"
}

function logger_debug
{
    logger_log_msg "debug" "$1"
}

function logger_info
{
    logger_log_msg "info" "$1"
}

function logger_warn
{
    logger_log_msg "warning" "$1"
}

function logger_error
{
    logger_log_msg "error" "$1"
}

