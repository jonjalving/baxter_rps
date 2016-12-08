#!/usr/bin/env python  
import cv2
import numpy as np
import time
import rospy
import bisect
import std_msgs.msg

rospy.init_node('hand_detector')
pub = rospy.Publisher('user_hand', std_msgs.msg.String, queue_size=1)

while not rospy.is_shutdown():
	pub.publish("rock")