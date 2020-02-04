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
from ..util import wait_for_position_estimator, reset_estimator, check_battery, start_console


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
        #    cf.param.set_value('ring.effect', '13')

            #set_led_color(cf, [0,0,0])

        #    pc.go_to(0, 0, 1)

            #pc.go_to(x * box_size, y * box_size, z * box_size + 1)


    #        set_led_color(cf, [0,0,0])
            #pc.go_to(x * box_size,y * box_size,0.1)
            # Make sure that the last packet leaves before the link is closed
            # since the message queue is not flushed before closing
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
   URI2,
   URI3,
   URI4
}

# The "names" We have assigned to the drones for logging
names = {
  URI1: ["Alice"],
  URI2: ["Bob"],
  URI3: ["Carol"],
  URI4: ["Doug"]
}

def print_errors(func):
    """
    This function is neccesary even though it really shouldn't be.

    There are two functions for running code on multiple drones, parallel and
    parallel_safe. You should ALWAYS use parallel_safe.

    All that parallel does is run parallel_safe but catches any errors that occur
    and ignores them. And this is ALL errors, even errors in your code that you
    should know about and fix.
    
    parallel_safe instead throws the errors (which is good). However, it never
    actually prints what the error is, so this function wraps any other function
    so that it actually prints the errors that occured.

    use like the following:
    swarm.parallel_safe(print_errors(start_console), args_dict=names)

    """

    try:
        func()
    except Exception as e:
        sys.exit(str(e))

def start_console(scf, name):
    """
    Logs console messages sent by the drone

    This implementation of logging is a little lazy, because the messages
    come in chunks, sometimes the one message is split over multiple lines.

    :param scf: SyncCrazyflie object
    :param name: name of the drone to prepend to every log
    """
    console = Console(scf.cf)

    def incoming(message):
        print(name + ": " + message)

    console.receivedChar.add_callback(incoming)


def check_battery(scf, name):
    """
      Checks the battery level. If the battery is too low, it prints an error
      and returns false, otherwise it returns true.

      Too low is considered to be 3.4 volts

      :param scf: SyncCrazyflie object
      :param name: The "Name" for logging
    """
    print("Checking battery")

    log_config = LogConfig(name = 'Battery', period_in_ms=500)
    log_config.add_variable('pm.vbat', 'float')

    with SyncLogger(scf, log_config) as logger:
      for log_entry in logger:
          print(name + ": battery at " + str(log_entry[1]['pm.vbat']))
          if log_entry[1]['pm.vbat'] > 3.4:
              print(name + ": Battery at good level")
              return True
          else:
              print(name + ": Battery too low")
              return False

if __name__ == '__main__':
    cflib.crtp.init_drivers(enable_debug_driver=False)
    factory = CachedCfFactory(rw_cache='./cache')
    with Swarm(uris, factory=factory) as swarm:
        swarm.parallel_safe(start_console, args_dict=names)
        swarm.parallel_safe(check_battery, args_dict=names)
        swarm.parallel_safe(reset_estimator)
        swarm.parallel_safe(run_shared_sequence, args_dict=positions)
        time.sleep(200)
