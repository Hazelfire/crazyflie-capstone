from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncLogger import SyncLogger
from cflib.crazyflie.console import Console
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie

import time

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

class MidLevelCommander():
    @print_errors
    def __init__(self, crazyflie=None, name="Crazyflie"):

        self.cf = crazyflie
        self.is_battery_low = False
        self.low_battery_threshold = 3.4

        if not crazyflie:
            self.cf = Crazyflie()

        if isinstance(crazyflie, SyncCrazyflie):
            self.cf = crazyflie.cf

        self.name = name
        
        if not self.check_battery():
            self.low_battery = True
            raise LowBatteryException

        self.start_console()
        self.start_battery_monitoring()

    @print_errors
    def start_console(self):
        """
        Logs console messages sent by the drone

        This implementation of logging is a little lazy, because the messages
        come in chunks, sometimes the one message is split over multiple lines.

        :param scf: SyncCrazyflie object
        :param name: name of the drone to prepend to every log
        """
        console = Console(self.cf)

        def incoming(message):
            print(self.name + ": " + message)

        console.receivedChar.add_callback(incoming)

    @print_errors
    def start_battery_monitoring(self):
        log_conf = LogConfig(name='Battery', period_in_ms=500)
        log_conf.add_variable('pm.vbat', 'float')

        self.cf.log.add_config(log_conf)
        log_conf.data_received_cb.add_callback(self.battery_callback)
        log_conf.start()

    @print_errors
    def battery_callback(self, timestamp, data, logconf):
        voltage = data['pm.vbat']

        if voltage <= self.low_battery_threshold:
            self.is_battery_low = True

            position = get_current_position()
            self.cf.commander.send_position_setpoint(position.x,
                                                     position.y,
                                                     0,
                                                     0)

            print(self.name + ": Battery low, landing")

    @print_errors
    def get_current_position(self):
        pass

    @print_errors
    def goto(self, x, y, z, yaw):
        if not self.is_battery_low:
            self.cf.commander.send_position_setpoint(x, y, z, yaw)

    @print_errors
    def check_battery(self):
        """
          Checks the battery level. If the battery is too low, it prints an error
          and returns false, otherwise it returns true.

          :param scf: SyncCrazyflie object
          :param name: The "Name" for logging
        """
        print("Checking battery")

        log_config = LogConfig(name = 'Battery', period_in_ms=500)
        log_config.add_variable('pm.vbat', 'float')

        with SyncLogger(self.cf, log_config) as logger:
          for log_entry in logger:
              print(self.name + ": battery at " + str(log_entry[1]['pm.vbat']))
              if log_entry[1]['pm.vbat'] > self.low_battery_threshold:
                  print(self.name + ": Battery at good level")
                  return True
              else:
                  print(self.name + ": Battery too low")
                  return False

class LowBatteryException(Exception):
    pass
