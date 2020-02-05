#!/usr/bin/env python3
"""
Author: Sam Nolan

This simple example moves the drones into a tetrahedron shape, then rotates the
shape along the x axis. It currently uses 4 drones to mark the corners of the
tetrahedron.

"""
import time

import cflib.crtp
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.console import Console
from cflib.crazyflie.swarm import CachedCfFactory
from cflib.crazyflie.swarm import Swarm
from cflib.crazyflie.syncLogger import SyncLogger
from cflib.positioning.position_hl_commander import PositionHlCommander
import math
from cfdemos.util import wait_for_position_estimator, reset_estimator, check_battery, start_console, print_errors


def run_shared_sequence(scf, x, y, z):
    print("Running sequence")
    cf = scf.cf

    try:
        box_size = 0.5
        
        for i in range(20):
            cf.commander.send_position_setpoint(x * box_size,
                                                y * box_size,
                                                z * box_size + 1,
                                                0)
            time.sleep(0.2)

        # This particular combination of sin and cosine is a rotation matrix, and will rotate the drones around the x axis
        for i in range(50):
            cf.commander.send_position_setpoint(x * box_size,
                                                y * box_size * math.cos(2 * math.pi / 50 * i) + z*box_size * math.sin(2*math.pi / 50 * i),
                                                -y* box_size * math.sin(2*math.pi / 50 * i) +z * box_size * math.cos(2 * math.pi / 50 * i) + 1,
                                                0)
            time.sleep(0.2)

        for i in range(20):
            cf.commander.send_position_setpoint(x * box_size,
                                                y * box_size,
                                                0.1,
                                                0)
            time.sleep(0.2)
    except Exception as e:
        print(e)


# Addresses for the drones
URI1 = 'radio://0/80/2M/A0A0A0A0AA'
URI2 = 'radio://0/80/2M/A0A0A0A0AB'
URI3 = 'radio://0/80/2M/A0A0A0A0AC'
URI4 = 'radio://0/80/2M/A0A0A0A0AD'

# Positions for the drones to fly to. This dictionary is passed to args_dict in
# parallel_safe. The array maps to the 2nd, 3rd and 4th arguments to the function
# (x, y and z above)
#
# These positions map out a tetrahedron

positions = {
  URI4: [0, (math.sqrt(2))/2, 0],
  URI2: [-0.5, -(math.sqrt(2))/2, 0],
  URI3: [0.5, -(math.sqrt(2))/2, 0],
  URI1: [0, 0, math.sqrt(2)/2]
}

# The drones you wish to include within the test. If you wish to not include
# a drone, simply remove them from this set
uris = {
   URI1,
   #URI2,
   #URI3,
   #URI4
}

# The "names" We have assigned to the drones for logging
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
        swarm.parallel_safe(run_shared_sequence, args_dict=positions)
        time.sleep(200)
