#!/usr/bin/python

import numpy as np
import rospy
import time

from nav_msgs.msg import Odometry
from geometry_msgs.msg import Pose, Twist
from std_msgs.msg import Float64
import argparse

parser = argparse.ArgumentParser(description="Reward node for RL framework")
parser.add_argument('-r', help='radius distance from the target', dest='radius', type=float, default=2.0)
parser.add_argument('-v', help='rotational velocity around the target', dest='velocity', type=float, default=1.0)

args, unknown = parser.parse_known_args()

print(args)
print(unknown)

buffodom = list()
def callbackODOMETRY(odom) :
	buffodom.append(odom)
	


continuer = True
def shutdown() :
	continuer = False

rospy.init_node('reward_node', anonymous=False)
rospy.on_shutdown(shutdown)

subODOM = rospy.Subscriber( '/robot_model_teleop_0/odom_diffdrive', Odometry, callbackODOMETRY )
pubR = rospy.Publisher('/RL/reward',Float64,queue_size=10)


rate = rospy.Rate(20)

todom = None
tr = Float64()
tr.data = 0.0

while continuer :
	
	if len(buffodom) :
		todom = buffodom[-1]
		del buffodom[:]
		
		#gather information :
		cp = todom.pose.pose.position
		ct = todom.twist.twist
		
		#let us compute the rewards to publish :
		radius = np.sqrt( cp.x**2+cp.y**2 )
		rp = 100*np.sqrt(ct.linear.x**2+ct.linear.y**2)#(radius-args.radius)**2
		#rt = ( np.sqrt(ct.linear.x**2+ct.linear.y**2) - args.velocity )**2
		rt = 100*(ct.angular.z - 0.05)**2
		lambdap = 0.8
		tr.data = 1.0/(1.0+rt+rp)#lambdap*rp+(1-lambdap)*rt
		
	if tr is not None :
		pubR.publish(tr)
	
	if continuer :	
		rate.sleep()


