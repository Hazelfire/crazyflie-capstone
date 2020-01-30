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


def activate_mellinger_controller(scf, use_mellinger):
    controller = 1
    if use_mellinger:
        controller = 2
    scf.cf.param.set_value('stabilizer.controller', controller)


def run_shared_sequence(scf, x, y, z):
    print("Running sequence")
    #activate_mellinger_controller(scf, False)
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


URI1 = 'radio://0/80/2M/A0A0A0A0AA'
URI2 = 'radio://0/80/2M/A0A0A0A0AB'
URI3 = 'radio://0/80/2M/A0A0A0A0AC'
URI4 = 'radio://0/80/2M/A0A0A0A0AD'

positions = {
  URI4: [0, (math.sqrt(2))/2, 0],
  URI2: [-0.5, -(math.sqrt(2))/2, 0],
  URI3: [0.5, -(math.sqrt(2))/2, 0],
  URI1: [0, 0, math.sqrt(2)/2]
}

uris = {
   URI1,
   URI2,
   URI3,
   URI4
}

names = {
  URI1: ["Alice"],
  URI2: ["Bob"],
  URI3: ["Carol"],
  URI4: ["Doug"]
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
    print("Cecking battery")

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
        #swarm.parallel_safe(activate_high_level_commander)
        swarm.parallel_safe(start_console, args_dict=names)
        swarm.parallel_safe(start_battery, args_dict=names)
        swarm.parallel_safe(reset_estimator)
        swarm.parallel_safe(run_shared_sequence, args_dict=positions)
        time.sleep(200)
