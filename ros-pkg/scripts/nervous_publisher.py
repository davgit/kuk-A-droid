#!/usr/bin/env python
#
# Copyright 2013 Arn-O. See the LICENSE file at the top-level directory of this
# distribution and at
# https://github.com/Arn-O/kuk-A-droid/blob/master/LICENSE.

'''
This program is a component of the kuk-A-droid project.
It will publish to ROS topics the valuation of the emotions and the behaviors.
The values can come from the onboarded device (aware mode) or from the teleop
program (zombie mode).
'''

import roslib; roslib.load_manifest('kuk_a_droid')
import argparse

from kuk_a_droid.msg import *
import rospy

# global constants
# ROS parameters
NODE_NAME = 'nervous_system'
PUBLISHER_NAME = 'nervous_states'
DEFAULT_FREQUENCY = 25

# affective parameter
NERVOUS_MODES = ['aware', 'zombie']
DEFAULT_NERVOUS_MODE = 'aware'
# note: emotions and behaviors are listed in the following orders
# emotions = anger frustration fear distress disgust sorrow surprise interest calm boredom joy
# behaviors = seek-people seek-toy sleep
EMOTIONS_DICT = {'anger':0, 'frustration':1, 'fear':2, 'distress':3,
        'disgust':4, 'sorrow':5, 'surprise':6, 'interest':7, 'calm':8,
        'boredom':9, 'joy':10}
BEHAVIORS_DICT = {'seek-people':0, 'seek-toy':1, 'sleep':2}

DEFAULT_EMOTION = 'calm'
DEFAULT_BEHAVIOR = 'sleep'

def stop_node():
    '''Clean stuff here.'''
    rospy.delete_param('~mode')
    rospy.logwarn('Nervous publisher has stopped - Bye!')

def get_nerv_msg(emotions, behaviors):
    '''Convert emotions and behaviors lists to msg'''
    emot_param = Emotions(*emotions)
    behav_param = Behaviors(*behaviors)
    nerv_msg = NervStates(emot_param, behav_param)
    return nerv_msg

def nervous_publisher(freq, emotions, behaviors):
    '''Publisher loop'''
    pub = rospy.Publisher(PUBLISHER_NAME, NervStates)
    while not rospy.is_shutdown():
        msg = get_nerv_msg(emotions, behaviors)
        pub.publish(msg)
        rospy.sleep(1.0 / freq)

def main():
    '''Where everything starts.'''
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mode",
            choices=NERVOUS_MODES,
            default=DEFAULT_NERVOUS_MODE,
            help='aware = autonomous / zombie = teleop')
    parser.add_argument("-f", "--frequency",
            type=int,
            default=DEFAULT_FREQUENCY,
            help='nervous publisher frequency')
    parser.add_argument("-e", "--emotion",
            choices=EMOTIONS_DICT.keys(),
            default=DEFAULT_EMOTION,
            help='emotion')
    parser.add_argument("-a", "--activation",
            type=int,
            default=1000,
            help='level of activation of the emotion (max = 1.000)')

    args = parser.parse_args()
    nervous_mode = args.mode
    pub_freq = args.frequency

    emotions = [0] * 11
    behaviors = [0] * 3
    emotions[EMOTIONS_DICT.get(args.emotion)] = args.activation
        
    rospy.init_node(NODE_NAME)
    rospy.on_shutdown(stop_node)
    rospy.set_param('~mode', nervous_mode)
    rospy.loginfo('Nervous system started in %s mode, this can be changed using services', nervous_mode)
    
    try:
        nervous_publisher(pub_freq, emotions, behaviors)
    except rospy.ROSInterruptException:
        pass

if __name__ == '__main__':
    main()
