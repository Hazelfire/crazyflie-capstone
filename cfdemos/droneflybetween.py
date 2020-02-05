#!/usr/bin/env python3
"""
This demonstration looks for two VIVE trackers and gets the drone to fly
halfway a little above halfway between the two.

It uses the low level commander, and requires SteamVR to be running
"""

import sys
import time

import openvr

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.syncLogger import SyncLogger
from cflib.positioning.position_hl_commander import PositionHlCommander
from cfdemos.util import wait_for_position_estimator, reset_estimator

# URI to the Crazyflie to connect to
uri = 'radio://0/80/2M/A0A0A0A0AA'


vr = openvr.init(openvr.VRApplication_Other)


# Find the two VIVE trackers
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
            

if tracker1 is None:
   sys.exit("Could not find any trackers, exiting")
   
if tracker2 is None:
    sys.exit("Could only find one tracker, exiting")

def get_tracker_pos(tracker):
    """
    Gets the position of a vive tracker and transforms it into the crazyflie's coordinate space
    """
    poses = vr.getDeviceToAbsoluteTrackingPose(
            openvr.TrackingUniverseStanding, 0,
            openvr.k_unMaxTrackedDeviceCount)

    controller_pose = poses[tracker]
    pose = controller_pose.mDeviceToAbsoluteTracking
        
    pos = [-1*pose[2][3], -1*pose[0][3], pose[1][3]]
    return pos
    
    
def run_sequence(scf):
    """
    Flies to the midpoint of the two controller's
    """
    cf = scf.cf
    height_above_center = 0.1
    while True:
                
        poses = vr.getDeviceToAbsoluteTrackingPose(
            openvr.TrackingUniverseStanding, 0,
            openvr.k_unMaxTrackedDeviceCount)

        pos1 = get_tracker_pos(tracker1)
        pos2 = get_tracker_pos(tracker2)
        setpoint = [(pos1[0] + pos2[0]) / 2,(pos1[1] + pos2[1]) / 2,(pos1[2] + pos2[2]) / 2 + height_above_center]
        
        scf.cf.commander.send_position_setpoint(setpoint[0], setpoint[1], setpoint[2], 0)
        
    pc.go_to(0.0, 0.0, 0.0)

    # Make sure that the last packet leaves before the link is closed
    # since the message queue is not flushed before closing
    time.sleep(0.1)

print("Starting")
if __name__ == '__main__':
    cflib.crtp.init_drivers(enable_debug_driver=False)

    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
        reset_estimator(scf)
        run_sequence(scf)

    openvr.shutdown()
