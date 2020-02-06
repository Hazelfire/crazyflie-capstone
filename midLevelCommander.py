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
    def __init__(self, crazyflie=None, name="Crazyflie"):

        self.cf = crazyflie

        if not crazyflie:
            self.cf = Crazyflie()

        if isinstance(crazyflie, SyncCrazyflie):
            self.cf = crazyflie.cf

        self.name = name
        
        if not self.check_initial_battery(self.cf, self.name):
            raise LowBatteryException

        self.start_console(self.cf, self.name)

    @print_errors
    def start_console(self, cf, name):
        """
        Logs console messages sent by the drone

        This implementation of logging is a little lazy, because the messages
        come in chunks, sometimes the one message is split over multiple lines.

        :param scf: SyncCrazyflie object
        :param name: name of the drone to prepend to every log
        """
        console = Console(cf)

        def incoming(message):
            print(name + ": " + message)

        console.receivedChar.add_callback(incoming)

    @print_errors
    def check_initial_battery(self, cf, name):
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

        with SyncLogger(cf, log_config) as logger:
          for log_entry in logger:
              print(name + ": battery at " + str(log_entry[1]['pm.vbat']))
              if log_entry[1]['pm.vbat'] > 3.4:
                  print(name + ": Battery at good level")
                  return True
              else:
                  print(name + ": Battery too low")
                  return False

class LowBatteryException(Exception):
    pass
