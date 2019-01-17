# profiling_late.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
#

'''
Module to enable profiling timepoints. This module is loaded
only if the configuration file exists, see profiling.py for more information
'''

import os
import sys
import yaml
import cProfile
from kano.logging import logger
from kano.profiling import CONF_FILE

conf = None
myProfile = cProfile.Profile()
app_name = sys.argv[0]
point_current = ""


def load_config():
    global conf

    # load the configuration file
    with open(CONF_FILE, 'r') as inp_conf:
        conf = yaml.load(inp_conf)


def has_key(d, k):
    return type(d) is dict and k in d


def declare_timepoint(name, isStart):
    global myProfile
    global point_current
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
                    if point_current:
                        logger.error(
                            'Stop profiling for point "{0}" and do "{1}" '
                            'instead'
                            .format(point_current, name)
                        )
                        myProfile.disable()
                        myProfile.clear()
                    point_current = name
                    myProfile.enable()
                else:
                    if point_current != name:
                        logger.error(
                            'Can\'t stop point "{0}" since a profiling '
                            'session for "{1}" is being run'
                            .format(name, point_current)
                        )
                    else:
                        myProfile.disable()
                        # Check if the statfile location in specified
                        if ct['python']['statfile']:
                            try:
                                myProfile.dump_stats(ct['python']['statfile'])
                            except IOError as err:
                                if err.errno == 2:
                                    logger.error(
                                        'Path to "{}" probably does not exist'
                                        .format(ct['python']['statfile'])
                                    )
                                else:
                                    logger.error(
                                        'dump_stats IOError: errno:{0}: {1} '
                                        .format(err.errno, err.strerror)
                                    )
                        else:
                            logger.error(
                                'No statfile entry in profiling conf file "{}"'
                                .format(CONF_FILE)
                            )
                        myProfile.clear()
                        point_current = ""
            else:
                logger.info(
                    'Profiling conf file doesnt enable the Python '
                    'profiler for point {} at app {}'
                    .format(name, app_name)
                )

            # Check if we want to run some other command at this timepoint
            if isStart and has_key(ct, 'start_exec'):
                cmd = ct['start_exec']
                os.system(cmd)
            if not isStart and has_key(ct, 'end_exec'):
                cmd = ct['end_exec']
                os.system(cmd)
        else:
            logger.info(
                'Profiling conf file doesnt include point:{} for app {}'
                .format(name, app_name)
            )
    else:
        logger.info(
            'Profiling conf file doesnt include app:{}'.format(app_name)
        )

    logger.debug(
        'timepoint ' + name,
        transition=name,
        isStart=isStart,
        cmd=cmd,
        pythonProfile=pythonProfile
    )
