#!/usr/bin/env python3
# Demo that makes one Crazyflie take off 30cm above the first controller found
# Using the controller trigger it is then possible to 'grab' the Crazyflie
# and to make it move.
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

# URI to the Crazyflie to connect to
uri = 'radio://0/80/2M/A0A0A0A0AA'

print('Opening')
print('Opened')

# Find first controller or tracker
controllerId = None



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


def get_path():
    path = sys.argv[1]
    contents = open(path, "r").readlines()
    vertices = [line for line in contents if line.startswith("v ")]
    elements = [[float(coordinate) for coordinate in vertex.split(" ")[1:]] for vertex in vertices]
    return elements
    
    

def pos_distance(pa, pb):
    def squared(x): 
        return x * x
    return math.sqrt(squared(pa[0] - pb[0]) + squared(pa[1] - pb[1]) + squared(pa[2] - pb[2]))

def set_led_color(cf, color):

    # Get LED memory and write to it
    mem = cf.mem.get_mems(MemoryElement.TYPE_DRIVER_LED)
    if len(mem) > 0:
        for i in range(12):
            mem[0].leds[i].set(r=color[0], g=color[1], b=color[2])
        mem[0].write_data(None)


def run_sequence(scf):
    cf = scf.cf
    with PositionHlCommander(scf, default_velocity=0.1) as pc:
        path = get_path()
        cf.param.set_value('ring.effect', '13')

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


print(get_path())

if __name__ == '__main__':
    cflib.crtp.init_drivers(enable_debug_driver=False)

    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
        reset_estimator(scf)
        run_sequence(scf)

