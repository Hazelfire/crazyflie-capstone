#!/usr/bin/env python3
"""
Author: Sam Nolan

This example demonstrates a drones precise ability to represent the beating of
a heart while flying. The drone moving back and forward represents the lub-dub
of heartbeat
"""
import time

import cflib.crtp
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.console import Console
from cflib.crazyflie.swarm import CachedCfFactory
from cflib.crazyflie.swarm import Swarm
import math
import random
# Util class, contains important functions that can be copied to other projects
from cfdemos.util import wait_for_position_estimator, reset_estimator, print_errors, start_console, check_battery

@print_errors
def run_shared_sequence(scf):
    """
    Runs the heartbeat sequence
    """

    print("Running sequence")
    cf = scf.cf

    height = 1
    heartbeat_size = 0.05
    
    # This takes off the drone to (height)m above the ground
    # The command is send 20 times every 0.2 seconds. This
    # repeating of the same command is becau
    for i in range(20):
        cf.commander.send_position_setpoint(0,
                                            0,
                                            height,
                                            0)
        time.sleep(0.2)

    for i in range(100):
        if i % 5 == 0:
            cf.commander.send_position_setpoint(- heartbeat_size, 
                                                0,
                                                height,
                                                0)
        elif i % 5 == 1:
            cf.commander.send_position_setpoint(heartbeat_size, 
                                                0,
                                                height,
                                                0)
        else:
            cf.commander.send_position_setpoint(0,
                                                0,
                                                height,
                                                0)

        time.sleep(0.2)

    for i in range(20):
        cf.commander.send_position_setpoint(0,
                                            0,
                                            0.1,
                                            0)
        time.sleep(0.2)


URI1 = 'radio://0/80/2M/A0A0A0A0AA'
URI2 = 'radio://0/80/2M/A0A0A0A0AB'
URI3 = 'radio://0/80/2M/A0A0A0A0AC'
URI4 = 'radio://0/80/2M/A0A0A0A0AD'

uris = {
   URI1,
   #URI2,
   #URI3,
   #URI4
}

names = {
  URI1: ["Alice"],
  URI2: ["Bob"],
  URI3: ["Carol"],
  URI4: ["Doug"]
}

if __name__ == '__main__':
    cflib.crtp.init_drivers(enable_debug_driver=False)
    factory = CachedCfFactory(rw_cache='./cache')
    with Swarm(uris, factory=factory) as swarm:
        swarm.parallel_safe(start_console, args_dict=names)
        swarm.parallel_safe(check_battery, args_dict=names)
        swarm.parallel_safe(reset_estimator)
        swarm.parallel_safe(run_shared_sequence)
