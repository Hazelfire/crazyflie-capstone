import logging
import time

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.mem import MemoryElement

URI = 'usb://0'

# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)

def set_led_color(cf, color):

    # Get LED memory and write to it
    mem = cf.mem.get_mems(MemoryElement.TYPE_DRIVER_LED)
    if len(mem) > 0:
        for i in range(12):
            mem[0].leds[i].set(r=color[0], g=color[1], b=color[2])
        mem[0].write_data(None)

if __name__ == '__main__':
    # Initialize the low-level drivers (don't list the debug drivers)
    cflib.crtp.init_drivers(enable_debug_driver=False)

    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:
        cf = scf.cf

        # Set virtual mem effect
        cf.param.set_value('ring.effect', '13')

        # Get LED memory and write to it
        mem = cf.mem.get_mems(MemoryElement.TYPE_DRIVER_LED)
        set_led_color(cf, color[100,0,0])

        time.sleep(2)
