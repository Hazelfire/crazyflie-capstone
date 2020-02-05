""" 
This module contains common utilities that can be reused among demos
"""

from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncLogger import SyncLogger
from cflib.crazyflie.console import Console
import time
import math

import cflib.crtp


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

@print_errors
def wait_for_position_estimator(scf):
    """
    This function was taken out of the crazyflie lighthouse openvr grab
    example found in the GitHub repository for cflib.
    crazyflie-lib-python/examples/lighthouse/lighthouse_openvr_grab.py

    It has the simple purpose of waiting until the kalman filter (the algorithm
    that the crazyflie uses to determine it's position) is fairly certain of it's
    position. (within the threshold, here 0.001m)

    :param scf: The SyncCrazyflie object for a particular crazyflie
    """
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

            if (max_x - min_x) < threshold and (
                    max_y - min_y) < threshold and (
                    max_z - min_z) < threshold:
                break

@print_errors
def reset_estimator(scf):
    """
    Resets the algorithm and waits for it to find the position again
    """
    cf = scf.cf
    cf.param.set_value('kalman.resetEstimation', '1')
    time.sleep(0.1)
    cf.param.set_value('kalman.resetEstimation', '0')
    wait_for_position_estimator(scf)

@print_errors
def position_callback(timestamp, data, logconf):
    x = data['kalman.stateX']
    y = data['kalman.stateY']
    z = data['kalman.stateZ']
    print('pos: ({}, {}, {})'.format(x, y, z))


@print_errors
def start_position_printing(scf):
    """
      Starts printing the postion of the drone
    """
    log_conf = LogConfig(name='Position', period_in_ms=500)
    log_conf.add_variable('kalman.stateX', 'float')
    log_conf.add_variable('kalman.stateY', 'float')
    log_conf.add_variable('kalman.stateZ', 'float')

    scf.cf.log.add_config(log_conf)
    log_conf.data_received_cb.add_callback(position_callback)
    log_conf.start()

@print_errors
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


@print_errors
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

def distance(x, y):
    """
    Finds the euclidiean distance between two lists x and y
    """
    return math.sqrt(sum([(p - q) ** 2 for p,q in zip(x,y)]))