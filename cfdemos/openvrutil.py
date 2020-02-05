"""
This module contains some utilities for contacting using openvr.

Using openvr requires that SteamVR is running on the computer that is being used.

Interestingly, all VIVE trackers connect to the computer via the headset. This means
that the headset has to be connected and running to any computer that you wish to use VIVE
with.
"""
import openvr
import sys

def init():
    """ Initialises openvr, returns a handle for use in all openvr calls """
    return openvr.init(openvr.VRApplication_Other)

def shutdown():
    return openvr.shutdown()
    
def find_two_trackers(vr):
    """
    Attempts to find 2 VIVE trackers. Make sure they are visible. You can see if SteamVR is
    picking them up by looking at the SteamVR status dialog
     
    :param vr: the vr object returned by init
    :return: a pair of tracker objects if successful. If none can be found, both of the objects are None, if one
             the second is None.
    """
    # Finds the trackers
    tracker1 = None
    tracker2 = None
    poses = vr.getDeviceToAbsoluteTrackingPose(openvr.TrackingUniverseStanding, 0,
                                               openvr.k_unMaxTrackedDeviceCount)
    for i in range(openvr.k_unMaxTrackedDeviceCount):
        if poses[i].bPoseIsValid:
            device_class = vr.getTrackedDeviceClass(i)
            if device_class == openvr.TrackedDeviceClass_GenericTracker:
                if tracker1 is not None:
                    tracker2 = i
                    break
                else:
                    tracker1 = i
                
    return tracker1, tracker2
    
 
def assert_has_two_trackers(vr):
    """
    Same as find_two_trackers, except will fail with a useful error message if the trackers are
    not found 
    """
    tracker1, tracker2 = find_two_trackers(vr)
    if tracker1 is None:
        sys.exit("Could not find any trackers, exiting")
    if tracker2 is None:
        sys.exit("Could only find one tracker, exiting")
    return tracker1, tracker2
     
def get_tracker_pos(vr, tracker):
    """
    Returns the position of a vive tracker within the coordinate space of the crazyflies
    """
    
    poses = vr.getDeviceToAbsoluteTrackingPose(
            openvr.TrackingUniverseStanding, 0,
            openvr.k_unMaxTrackedDeviceCount)

    controller_pose = poses[tracker]
    pose = controller_pose.mDeviceToAbsoluteTracking
        
    pos = [-1*pose[2][3], -1*pose[0][3], pose[1][3]]
    return pos    