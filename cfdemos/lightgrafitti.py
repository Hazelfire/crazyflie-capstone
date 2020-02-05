#!/usr/bin/env python3
# Demo that makes one Crazyflie take off 30cm above the first controller found
# Using the controller trigger it is then possible to 'grab' the Crazyflie
# and to make it move.
"""
Author: Sam Nolan
This demonstration draws a path specified by an .obj file (can be exported from
blender)

This demonstration uses the Position High Level commander as we found it has
better results.

The drone should first take off to it's starting position, then draw the path
specified, then fly back down to land.

Unlike the other demonstrations, this demo must be run with an argument indicating
the obj file that you want the drone to fly in, like

./lightgrafitti.py RMIT.obj
"""
import sys
import time
import math


import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.syncLogger import SyncLogger
from cflib.crazyflie.mem import MemoryElement
from cflib.positioning.position_hl_commander import PositionHlCommander
from cfdemos.util import wait_for_position_estimator, reset_estimator

# URI to the Crazyflie to connect to
uri = 'radio://0/80/2M/A0A0A0A0AB'

def get_path():
    """
    Very primitive path reading function.

    An .obj file simply contains a list of vertices and the lines that connect
    those vertices. This function simply takes all the vertices of the .obj
    file and goes to them in the order they appear in the file.

    If you specify a curve in blender, it should print the vertices in the file
    in the right order along the curve, so you can use such curves to specify
    paths to draw.

    closed shapes will also work, as done with the RMIT logo.

    :return: returns an list of 3 dimensional points (represented as lists of size 3)
    """
    if len(sys.argv) < 2:
        sys.exit("Argument required (obj flight path)")
    path = sys.argv[1]
    contents = open(path, "r").readlines()
    vertices = [line for line in contents if line.startswith("v ")]
    elements = [[float(coordinate) for coordinate in vertex.split(" ")[1:]] for vertex in vertices]
    return elements
    
    

def set_led_color(cf, color):
    """
    Sets the color of the light deck. 

    :param cf: The scf.cf from the SyncCrazyflie
    :param color: a list of size 3 indicating the color wanted in RGB
    """

    # Get LED memory and write to it
    mem = cf.mem.get_mems(MemoryElement.TYPE_DRIVER_LED)
    if len(mem) > 0:
        for i in range(12):
            mem[0].leds[i].set(r=color[0], g=color[1], b=color[2])
        mem[0].write_data(None)

path = get_path()

def run_sequence(scf):
    """
    Flies in the given path
    """
    cf = scf.cf
    with PositionHlCommander(scf, default_velocity=0.1) as pc:
        cf.param.set_value('ring.effect', '13')
        # Starts with all the LEDs off
        set_led_color(cf, [0,0,0])


        
        pc.go_to(path[0][0], path[0][2], path[0][1])

        last_pos = path[0]
        set_led_color(cf, [0,100,0])
        for position in get_path():
            pc.go_to(position[0], position[2], position[1])
            last_pos = position


        set_led_color(cf, [0,0,0])
        pc.go_to(0,0,0.1)
        # Make sure that the last packet leaves before the link is closed
        # since the message queue is not flushed before closing
        time.sleep(0.1)


if __name__ == '__main__':
    cflib.crtp.init_drivers(enable_debug_driver=False)

    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
        reset_estimator(scf)
        run_sequence(scf)

