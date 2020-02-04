#!/usr/bin/env python3
# Demo that makes one Crazyflie take off 30cm above the first controller found
# Using the controller trigger it is then possible to 'grab' the Crazyflie
# and to make it move.
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
from matplotlib import style



# URI to the Crazyflie to connect to
uri = 'radio://0/80/2M'

print('Opening')
vr = openvr.init(openvr.VRApplication_Other)
print('Opened')

style.use('fivethirtyeight')

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)

# Find first controller or tracker
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
            

if tracker1 is None or tracker2 is None:
    print('Cannot find controller or tracker, exiting')
    sys.exit(1)




    




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

    wait_for_position_estimator(cf)


def position_callback(timestamp, data, logconf):
    x = data['kalman.stateX']
    y = data['kalman.stateY']
    z = data['kalman.stateZ']
    print('pos: ({}, {}, {})'.format(x, y, z))


def start_position_printing(scf):
    log_conf = LogConfig(name='Position', period_in_ms=500)
    log_conf.add_variable('kalman.stateX', 'float')
    log_conf.add_variable('kalman.stateY', 'float')
    log_conf.add_variable('kalman.stateZ', 'float')

    scf.cf.log.add_config(log_conf)
    log_conf.data_received_cb.add_callback(position_callback)
    log_conf.start()


def vector_substract(v0, v1):
    return [v0[0] - v1[0], v0[1] - v1[1], v0[2] - v1[2]]


def vector_add(v0, v1):
    return [v0[0] + v1[0], v0[1] + v1[1], v0[2] + v1[2]]


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
    return math.sqrt(squared(pos1[0] - pos2[0]) + squared(pos1[1] - pos2[1]) + squared(pos1[2] + pos1[2]))

def run_sequence():
    while True:
                
        poses = vr.getDeviceToAbsoluteTrackingPose(
            openvr.TrackingUniverseStanding, 0,
            openvr.k_unMaxTrackedDeviceCount)

        pos1 = get_tracker_pos(tracker1)
        pos2 = get_tracker_pos(tracker2)
        
        print(distance(pos1, pos2))
        time.sleep(0.1)

        
xs = []
ys = []
def animate(i):
    poses = vr.getDeviceToAbsoluteTrackingPose(
            openvr.TrackingUniverseStanding, 0,
            openvr.k_unMaxTrackedDeviceCount)

    pos1 = get_tracker_pos(tracker1)
    pos2 = get_tracker_pos(tracker2)
        
    print(distance(pos1, pos2))
  
    
    if len(xs) > 20:
        xs.pop(0)
        ys.pop(0)
    
    xs.append(i)
    ys.append(distance(pos1, pos2))
    ax1.clear()
    ax1.plot(xs, ys)        
        
print("Starting")
if __name__ == '__main__':
  #  cflib.crtp.init_drivers(enable_debug_driver=False)

    
    ani = animation.FuncAnimation(fig, animate, interval=100)
    plt.show()
    openvr.shutdown()
