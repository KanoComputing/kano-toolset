# profiling_late.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Module to enable profiling timepoints. This module is loaded
# only if the configuration file exists, see profiling.py for more information


import os
import sys
import yaml
import cProfile
from kano.logging import logger
from kano.profiling import CONF_FILE

# load the configuration file
conf = yaml.load(open(CONF_FILE, 'r'))
myProfile = None
app_name = sys.argv[0]


def has_key(d, k):
    return type(d) is dict and k in d


def declare_timepoint(name, isStart):
    global myProfile
    cmd = None
    pythonProfile = False

    if has_key(conf, app_name):
        if has_key(conf[app_name], name):
            ct = conf[app_name][name]

            # check if python profiler should be started for this timepoint
            if has_key(ct, 'python'):
                pythonProfile = True
                if isStart:
                    myProfile = cProfile.Profile()
                    myProfile.enable()
                else:
                    if myProfile is None:
                        logger.error(' timepoint '+name+' not started')
                    else:
                        myProfile.disable()
                        myProfile.dump_stats(ct['python']['statfile'])
                        myProfile = None

            # check if we want to run some other command at this timepoint
            if isStart and has_key(ct, 'start_exec'):
                cmd = ct['start_exec']
                os.system(cmd)
            if not isStart and has_key(ct, 'end_exec'):
                cmd = ct['end_exec']
                os.system(cmd)

    logger.debug('timepoint '+name, transition=name, isStart=isStart, cmd=cmd, pythonProfile=pythonProfile)
