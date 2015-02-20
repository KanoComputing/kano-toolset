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
with open(CONF_FILE, 'r') as inp_conf:
    conf = yaml.load(inp_conf)
myProfile = cProfile.Profile()
app_name = sys.argv[0]


def has_key(d, k):
    return type(d) is dict and k in d


def declare_timepoint(name, isStart):
    global myProfile
    cmd = None
    pythonProfile = False

    # Check if the app is contained in the profiling conf file
    if has_key(conf, app_name):
        # Check if the timepoint name is contained in the profiling conf file
        if has_key(conf[app_name], name):
            ct = conf[app_name][name]

            # Check if python profiler should be started for this timepoint
            if has_key(ct, 'python'):
                pythonProfile = True
                if isStart:
                    myProfile.enable()
                else:
                    if myProfile is None:
                        logger.error(' timepoint '+name+' not started')
                    else:
                        myProfile.disable()
                        # Check if the statfile location in specified
                        if ct['python']['statfile']:
                            myProfile.dump_stats(ct['python']['statfile'])
                        else:
                            logger.error('No statfile entry in profiling conf file')
                        myProfile.clear()
            else:
                logger.info('Profiling conf file doesnt enable the Python profiler for point {} at app {}'.format(name, app_name))

            # Check if we want to run some other command at this timepoint
            if isStart and has_key(ct, 'start_exec'):
                cmd = ct['start_exec']
                os.system(cmd)
            if not isStart and has_key(ct, 'end_exec'):
                cmd = ct['end_exec']
                os.system(cmd)
        else:
            logger.info('Profiling conf file doesnt include point:{} for app {}'.format(name, app_name))
    else:
        logger.info('Profiling conf file doesnt include app:{}'.format(app_name))

    logger.debug('timepoint '+name, transition=name, isStart=isStart, cmd=cmd, pythonProfile=pythonProfile)
