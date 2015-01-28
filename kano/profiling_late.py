# Module to enable profiling timepoints. This module is loaded
# only if the configuration file exists, see profiling.py for more information


import os
import sys
import yaml
import cProfile
from kano.logging import logger
from kano.profiling import CONF_FILE

# load the configuration file
conf = yaml.load(open(CONF_FILE, "r"))
myProfile=None
app_name=sys.argv[0]



def declare_timepoint(name,isStart):
    global myProfile
    logger.info(name,isStart=isStart)

    if conf.has_key(app_name):
        if conf[app_name].has_key(name):
            ct=conf[app_name][name]

            # check if python profiler should be started for this timepoint
            if ct.has_key('python'):
                if isStart:
                    myProfile=cProfile.Profile()
                    myProfile.enable()
                else:
                    if myProfile is None:
                        logger.error(" timepoint "+name+" not started")
                    else:
                        myProfile.disable()
                        myProfile.dump_stats(ct['python']['statfile'])
                        myProfile=None

            # check if we want to run some other command at this timepoint
            if isStart and ct.has_key('start_exec'):
                os.system(ct['start_exec'])
            if not isStart and ct.has_key('end_exec'):
                os.system(ct['end_exec'])



    
