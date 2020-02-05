#!/usr/bin/env python3
"""
Author: Sam Nolan
This demonstration shows using matplotlib to graph the distance between two
VIVE Trackers.

This demonstration requires having two VIVE trackers and running steam
VR connected to a headset.

This demonstration does not require connecting to a drone, connecting to a drone
will happen when you press "fly" on the interface

It also requires having matplotlib installed:
pip3 install --user matplotlib
"""

import sys
import time
import math

import openvr

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.syncLogger import SyncLogger
from cflib.positioning.position_hl_commander import PositionHlCommander

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button
from matplotlib import style
from cflib.crazyflie.console import Console
from cfdemos.util import print_errors, wait_for_position_estimator, reset_estimator, start_console, check_battery

    

# URI to the Crazyflie to connect to
uri = 'radio://0/80/2M/A0A0A0A0AA'

# Connect to Steam VR
vr = openvr.init(openvr.VRApplication_Other)

style.use('fivethirtyeight')

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)

# Finds the trackers
tracker1 = None
tracker2 = None
poses = vr.getDeviceToAbsoluteTrackingPose(openvr.TrackingUniverseStanding, 0,
                                           openvr.k_unMaxTrackedDeviceCount)
for i in range(openvr.k_unMaxTrackedDeviceCount):
    if poses[i].bPoseIsValid:
        device_class = vr.getTrackedDeviceClass(i)
        if device_class == openvr.TrackedDeviceClass_GenericTracker:
            if tracker1 is not None:
                if tracker2 is not None:
                    print('More than two controllers, exiting')
                    sys.exit(1)
                tracker2 = i
                break
            else:
                tracker1 = i
            
# If the trackers cannot be found, error
if tracker1 is None or tracker2 is None:
    print('Cannot find controller or tracker, exiting')
    sys.exit(1)


def get_tracker_pos(tracker):
    poses = vr.getDeviceToAbsoluteTrackingPose(
            openvr.TrackingUniverseStanding, 0,
            openvr.k_unMaxTrackedDeviceCount)

    controller_pose = poses[tracker]
    pose = controller_pose.mDeviceToAbsoluteTracking
        
    pos = [-1*pose[2][3], -1*pose[0][3], pose[1][3]]
    return pos
    
def squared(x):
  return x * x
    
def distance(pos1, pos2):
    return math.sqrt(squared(pos1[0] - pos2[0]) + squared(pos1[1] - pos2[1]) + squared(pos1[2] - pos2[2]))
    

xs = []
time_series_smooth = []
ys = []
flying = False
base = 0
scf = None
high = 2
low = 0

def change_fly(event):
    """
    What happens when you press the fly button on the matplotlib interface.

    This button toggles flying. If pressed while still flying it turns lands
    the drone and turns off
    """
   
    global flying, scf
    scf = SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache'))
    scf.open_link()
    reset_estimator(scf)
    check_battery(scf, "Drone")
    start_console(scf, "Drone")
    flying = not flying
    if not flying and scf:
        scf.cf.commander.send_position_setpoint(0,
                                                0,
                                                0,
                                                0)

def animate(i):
    """
    The clock method of matplotlib
    """
    poses = vr.getDeviceToAbsoluteTrackingPose(
            openvr.TrackingUniverseStanding, 0,
            openvr.k_unMaxTrackedDeviceCount)

    pos1 = get_tracker_pos(tracker1)
    pos2 = get_tracker_pos(tracker2)
    print(distance(pos1, pos2))
    
    if len(time_series_smooth) < 5:
        time_series_smooth.append(distance(pos1, pos2))
    else:
        time_series_smooth.pop(0)
        time_series_smooth.append(distance(pos1, pos2))
        
        average = sum(time_series_smooth) / len(time_series_smooth)
            
        if len(xs) > 20:
            xs.pop(0)
            ys.pop(0)
        
        xs.append(i)
        ys.append(average)
        ax1.clear()
        ax1.plot(xs, ys)
        lowest_point = 0.5
        highest_point = 1.5
        percentage = max(min((average - low ) / (high - low), 1), 0)
        fly_height = lowest_point + percentage
        if flying and scf:
          
            scf.cf.commander.send_position_setpoint(0,
                                                    0,
                                                    fly_height,
                                                    0)      
    ax1.set_ylim((low, high))

    
def set_high(event):
    global high
    high = time_series_smooth[-1]
    
def set_low(event):
    global low
    low = time_series_smooth[-1]
    
print("Starting")
if __name__ == '__main__':
    cflib.crtp.init_drivers(enable_debug_driver=False)

    cflib.crtp.init_drivers(enable_debug_driver=False)

    
        
    scf = None
    ani = animation.FuncAnimation(fig, animate, interval=100)
    axfly = plt.axes([0.7, 0, 0.1, 0.075])
    axlow = plt.axes([0.75, 0, 0.1, 0.075])
    axhigh = plt.axes([0.8, 0, 0.1, 0.075])
    bfly = Button(axfly, 'Fly')
    bhigh = Button(axhigh, 'High')
    blow = Button(axlow, 'Low')
    bfly.on_clicked(change_fly)
    bhigh.on_clicked(set_high)
    blow.on_clicked(set_low)
    
    plt.show()
    openvr.shutdown()
