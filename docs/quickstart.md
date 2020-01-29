# Quickstart on Crazyflie drone positioning using the lighthouse positioning system

This documentation is meant to get you up and running with the lighthouse positioning system with the crazyflie.

Requirements:
Setup:
  - A computer with Steam VR and a VIVE headset (only for setup)
  - Git

Flying:
  - A crazyflie radio
  - A computer with python 3 and make installed
  - An X-box controller (for manual flight with position assist)
  - An HTC vive controller (for flying using the grab example)

## Setup.

This sets up a crazyflie to a paricular pair of lighthouses. If you want to
pair the crazyflie to another pair of lighthouses, this phase must be repeated.

### Setting the origin
The step of setting the origin is not neccesary, but it is good to know the center
of your coordinate space before flying. We mark the origin and axes with tape.

To set the origin of a lighthouse system. Get a windows computer and connect the
headset to it. Open Steam VR on the computer (Steam VR is a tool that can be downloaded
from steam).

[Follow path to set origin]

Place the headset in the position you want your origin, and the direction that 
you want your positive X to be. The positive Y will go to the right of the headset
and positive Z will go up.

### Encoding the position of the lighthouses into the crazyflie firmware

Keep Steam VR running, and do the following on the computer with Steam VR

To find the position of the lighthouse, check out a copy of the crazyflie firmware

https://github.com/bitcraze/crazyflie-firmware

Then with python 3. Install openvr and numpy. Then run the script found in

```
crazyflie-firmware/tools/lighthouse/get_bs_position.py
```

This will give an output that look like this:

```
Openning OpenVR
OpenVR Oppened
Origin: {} [0, 0, 0]
-------------------------------
{.origin = {-1.421995, 2.188835, -1.382714, }, .mat = {{-0.773449, 0.339506, -0.535269, }, {0.027097, 0.861399, 0.507206, }, {0.633280, 0.377794, -0.675447, }, }},
{.origin = {1.311097, 2.224771, 1.318952, }, .mat = {{0.641178, -0.457615, 0.616019, }, {0.029892, 0.817028, 0.575823, }, {-0.766810, -0.350791, 0.537539, }, }},
```

The last 2 lines here are positions and rotations that can be copied into the
firmware for the lighthouse deck.

Copy the results there, and paste them into 

```
crazyflie-firmare/src/deck/drivers/src/lighthouse.c
```

inside the lighthouseBaseStationsGeometry variable.

Also, make sure you comment out the `DISABLE_LIGHTHOUSE_DRIVER` lines before it

```
//#ifndef DISABLE_LIGHTHOUSE_DRIVER
//  #define DISABLE_LIGHTHOUSE_DRIVER 1
//#endif
```

To enable the driver.

Compile the driver with `make`. Then, with the crazyflie radio connected and the
crazyflie booted into firmware mode, run `make cload` to flash the firmware
onto the drone.

## Testing the setup.

There are several ways to test the setup. As the crazyflie can fly in unexpected
ways if it is not set up correctly, we recommend being fairly certain that the
system works before flying.

### Checking the telemetry

The first thing to do is to start the crazyflie, with the lighthouse module installed
on top of it, within the play space. Make sure that nobody or
nothing is obstructing the crazyflie's view of the two lighthouses.

Then connect to the crazyflie with the crazyflie client. Setup instructions
can be found [here](). Make sure that you have the Look at the logs of the crazyflie. If you are getting
errors such "Estimator out of bounds, resetting" continously or it does not
say that it is ready to fly, then it has not been set up correctly, and we
reccomend that you check through the above steps (particularly commenting out
`DISABLE_LIGHTHOUSE_DRIVER`). If the drone says it is ready to fly, then continue
onto the next test.

### plotting position data
[Create a log group for position data]

### Flight assist.
Place the crazyflie back inside of the play space. On the crazyflie client, set
the assist mode to position hold. You need an xbox controller to fly the drone
using the pc client.

Here are the controls to fly a drone in position hold mode. Note 2 important things.

1. The controls are absolute and not relative to the direction that the drone
is facing. Pushing the left stick up will move the drone in the positive X no
matter what the yaw is

2. The drone will only hold it's position if the assist mode button is held
down, which is the right button. Note that these buttons are often the first
ones to detereiorate on an x-box controller, so if it is not working, you may
need to use another x-box controller or push down on that button with a little
more force than you might think.

Start flight by holding down the assist button, the drone, without any other
inputs should try to hover itself very slightly above the ground. If it does,
move it up off the ground using the right stick. The drone should hover in the
same position as long as you hold down the assist button.

The drone may drift slightly. This issue is generally fixed by restarting the drone
and ensuring that it is on a truly flat surface when it is trying to stabalise
itself.

The position hold is not likely going to be perfect.

If this works, it's worth trying out (almost) autonomous flight

### Semi autonomous flight, openvr grab sample

You will have to run this on a computer with Steam VR installed and running.

Clone the repo for cflib, which allows autonomous flying

```
https://github.com/bitcraze/crazyflie-lib-python
```

If you are on Linux, take note of the information in the README about how to
run these scripts without root, and install the package as per the README.

Open up SteamVR, and make sure that all items except one controller are visible
within SteamVR (visible of the lighthouse deck) Place that one controller on the
floor next to the crazyflie drone, about 20cm away.

Before doing this, be ready to press Ctrl+C on the python script to ensure that
you can stop the drone if it behaves strangely.

Turn the crazyflie on inside the space, and run the following:

```
python examples/lighthouse/lighthouse_openvr_grab.py
```

The drone should hover itself about 30cm above the controller. Take the controller
and use the switch at the back to drag the drone around. To stop it from flying,
bring it close to the ground and exit the script with Ctrl+C or similar.

### Fully autonomous flight, light grafitti pathfinding example.

Finally, this uses the code that we developed based off the grab system that
controls the drone to create a path.

First, open up a 3D modelling program such as Blender, and create a path (a line of
vertices, or a closed shape but curves also work). Keep in mind that 1 unit
in your software is equal to one meter of space, so ensure that you are not flying
too far in any particular direction, or underneath the earth (below z=0).

Export your file as a .obj file. Then put it in the same directory as this project

with the crazyflie radio attached, and cflib installed, run

```
python pathfind.py <exported_obj_file>
```

Wait, and it should follow the path slowly. If the LED deck is installed it will
light up when it is following your path and turn off when it is not. It should
safely fly itself up and down.
