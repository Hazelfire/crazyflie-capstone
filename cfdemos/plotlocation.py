"""
Author: Sam Nolan
This demonstration simply shows the ability to track a drone within 3D space
using matplotlib

Simply run this and connect to a drone to draw it's location.
"""
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.syncLogger import SyncLogger
from cfdemos.util import print_errors, reset_estimator, check_battery, start_console
from matplotlib import style

style.use('fivethirtyeight')
fig = plt.figure()
ax = Axes3D(fig)



ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

uri = 'radio://0/80/2M/A0A0A0A0AA'
x = 0
y = 0
z = 0

def animate(i):
    """
    Redraws the single point that is the drone on the scatter plot
    """
    ax.clear()
    ax.scatter([x], [y], [z])
    ax.set_ylim(-2, 2)
    ax.set_xlim(-2, 2)
    ax.set_zlim(0, 2)

@print_errors
def position_callback(timestamp, data, logconf):
    global x, y, z
    
    x = data['kalman.stateX']
    y = data['kalman.stateY']
    z = data['kalman.stateZ']

if __name__ == '__main__':
    cflib.crtp.init_drivers(enable_debug_driver=False)
    ani = FuncAnimation(fig, animate, interval=100)
    scf = SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache'))
    scf.open_link()
    
    # Add position tracking
    log_conf = LogConfig(name='Position', period_in_ms=100)
    log_conf.add_variable('kalman.stateX', 'float')
    log_conf.add_variable('kalman.stateY', 'float')
    log_conf.add_variable('kalman.stateZ', 'float')
    
    # Add log config to drone
    scf.cf.log.add_config(log_conf)
    log_conf.data_received_cb.add_callback(position_callback)
    log_conf.start()
    
    reset_estimator(scf)
    check_battery(scf, "Drone")
    start_console(scf, "Drone")
    plt.show()
