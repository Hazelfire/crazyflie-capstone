# -*- coding: utf-8 -*-
#
#     ||          ____  _ __
#  +------+      / __ )(_) /_______________ _____  ___
#  | 0xBC |     / __  / / __/ ___/ ___/ __ `/_  / / _ \
#  +------+    / /_/ / / /_/ /__/ /  / /_/ / / /_/  __/
#   ||  ||    /_____/_/\__/\___/_/   \__,_/ /___/\___/
#
#  Copyright (C) 2019 Bitcraze AB
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA  02110-1301, USA.
"""
Simple example of a swarm using the High level commander.

The swarm takes off and flies a synchronous square shape before landing.
The trajectories are relative to the starting positions and the Crazyfles can
be at any position on the floor when the script is started.

This example is intended to work with any absolute positioning system.
It aims at documenting how to use the High Level Commander together with
the Swarm class.
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

from ..midLevelCommander import MidLevelCommander

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

    or, equivalently, using python decorator syntax:
    
    @print_errors
    def start_console(scf, x, y, z)

    All functions called with scf in this file are decorated this way

    """

    def wraps(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e)
            raise e
    return wraps

def wait_for_position_estimator(scf):
    print('Waiting for estimator to find position...')

    log_config = LogConfig(name='Kalman Variance', period_in_ms=500)
    log_config.add_variable('kalman.varPX', 'float')
    log_config.add_variable('kalman.varPY', 'float')
    log_config.add_variable('kalman.varPZ', 'float')

    var_y_history = [1000] * 10
    var_x_history = [1000] * 10
    var_z_history = [1000] * 10

    threshold = 0.001

    with SyncLogger(scf, log_config) as logger:
        for log_entry in logger:
            data = log_entry[1]

            var_x_history.append(data['kalman.varPX'])
            var_x_history.pop(0)
            var_y_history.append(data['kalman.varPY'])
            var_y_history.pop(0)
            var_z_history.append(data['kalman.varPZ'])
            var_z_history.pop(0)

            min_x = min(var_x_history)
            max_x = max(var_x_history)
            min_y = min(var_y_history)
            max_y = max(var_y_history)
            min_z = min(var_z_history)
            max_z = max(var_z_history)

            # print("{} {} {}".
            #       format(max_x - min_x, max_y - min_y, max_z - min_z))

            if (max_x - min_x) < threshold and (
                    max_y - min_y) < threshold and (
                    max_z - min_z) < threshold:
                break


def reset_estimator(scf):
    cf = scf.cf
    cf.param.set_value('kalman.resetEstimation', '1')
    time.sleep(0.1)
    cf.param.set_value('kalman.resetEstimation', '0')
    wait_for_position_estimator(scf)


def activate_high_level_commander(scf):
    scf.cf.param.set_value('commander.enHighLevel', '1')

@print_errors
def activate_mid_level_commander(scf):
    MidLevelCommander(scf)

def activate_mellinger_controller(scf, use_mellinger):
    controller = 1
    if use_mellinger:
        controller = 2
    scf.cf.param.set_value('stabilizer.controller', controller)


def run_shared_sequence(scf):
    print("Running sequence")
    #activate_mellinger_controller(scf, False)
    cf = scf.cf

    box_size = 0.5
   
    try:
        for i in range(20):
            cf.commander.send_position_setpoint(0,
                                                0,
                                                box_size,
                                                0)
            time.sleep(0.2)

        for i in range(45):
            cf.commander.send_position_setpoint(math.cos(4 * math.pi * i / 45) * min(i * 4 / 45, 1) * box_size,
                                                math.sin(4 * math.pi * i / 45) * min(i * 4 / 45, 1) * box_size,
                                                box_size,
                                                -i * 32)
            time.sleep(0.2)

        for i in range(10):
            cf.commander.send_position_setpoint(0,
                                                0,
                                                box_size,
                                                0)
            time.sleep(0.2)

        for i in range(10):
            cf.commander.send_position_setpoint(0,
                                                0,
                                                0,
                                                0)
            time.sleep(0.1)
        #    cf.param.set_value('ring.effect', '13')

            #set_led_color(cf, [0,0,0])

        #    pc.go_to(0, 0, 1)

            #pc.go_to(x * box_size, y * box_size, z * box_size + 1)


    #        set_led_color(cf, [0,0,0])
            #pc.go_to(x * box_size,y * box_size,0.1)
            # Make sure that the last packet leaves before the link is closed
            # since the message queue is not flushed before closing
    except Exception as e:
        for i in range(20):
            cf.commander.send_position_setpoint(0,
                                                0,
                                                0,
                                                0)
            time.sleep(0.2)

        print(e)


URI1 = 'radio://0/80/2M/A0A0A0A0AA'

uris = {
   URI1,
}

names = {
    URI1: ["Alice"],
}

def start_console(scf, name):
    try:
        console = Console(scf.cf)

        def incoming(message):
            print(name + ": " + message)

        console.receivedChar.add_callback(incoming)
        

    except Exception as e:
        print(e)

def start_battery(scf, name ):
    print("Chcking battery")

    log_config = LogConfig(name = 'Battery', period_in_ms=500)
    log_config.add_variable('pm.vbat', 'float')

    with SyncLogger(scf, log_config) as logger:
      for log_entry in logger:
          print(name + ": " + str(log_entry[1]['pm.vbat']))
          if log_entry[1]['pm.vbat'] > 0.4:
              print("Good to go")
              break
          else:
              print("Battery too low")

if __name__ == '__main__':
    cflib.crtp.init_drivers(enable_debug_driver=False)
    factory = CachedCfFactory(rw_cache='./cache')
    with Swarm(uris, factory=factory) as swarm:
        swarm.parallel_safe(activate_mid_level_commander)
        swarm.parallel_safe(reset_estimator)
        swarm.parallel_safe(run_shared_sequence)
