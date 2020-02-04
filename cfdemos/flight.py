"""
This module contains utilities to help fly a drone. 


Notes on high and low level commanders:

There are two different ways to fly a drone. One is the normal commander (cflib/crazyflie/commander.py)
and the other is the "Position High level commander" (cflib/positioning/position_hl_commander.py)
The former is considered to be more "low level" than the latter, meaning that
the former provides more fine level control but is less practical to use than
the latter.

The high level commander offers the following services:
    - Automatic take off
    - Automatic landing after the procedure has been complete 
    - Control of the speed of the drone
    - Better accuracy in the movement of the drone

The big things that came up for using the high level commander is that it 
produced far better results for the drone ligh grafitti project than the low level
one, more accurately positioning it through space.

Using the high level commander however for demonstrations such as flying a drone
inbetween hands is a little clumsy, simply because the drone attempts to fly at a
constant speed even if your hands are not.

Using multilple drones with the high level commander was a disaster. Although
we cannot find reference to the code that performs this, on taking off, the drones
will always want to come about 50cm above the origin (0, 0, 0.5) as part of the
take of procedure. This causes drones to crash into each other if multiple are
trying to do it at the same time. As of such, for multiple drones we always use
the low level commander.

Unless it's a single drone trying to move in a very precise manner regardless
of speed, we opt to use the low level commander as we find it more reliable.

This module contains other tools to ensure that the flight of the drone is stable.
Such as

  - Checking the battery level

"""
