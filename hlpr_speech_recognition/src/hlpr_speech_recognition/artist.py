#!/usr/bin/env python  
import rospy
import math
import geometry_msgs.msg
from std_msgs.msg import String
from hlpr_speech_msgs.msg import StampedString
from hlpr_speech_msgs.srv import SpeechService
import speech_listener
import turtlesim.srv
import turtlesim.msg
import std_srvs.srv
import pickle
import numpy as np
import os



def publishVel(linear, angular, pub):
	'''
	Convenience function. Takes a linear and angular velocity
	and a publisher, creates a message, and publishes to that publisher
	The publisher should be cmd_vel or at leasttake a geometry Twist msg
	'''
	message = geometry_msgs.msg.Twist()
	message.linear.x = linear
	message.angular.z = angular
	pub.publish(message)

class Artist:
	'''
	Artist class controls a turtlesim to draw input passed to it on a screen.  It loads a dictionary
	of characters, each with a list of segments and asociated linear and angular velocities, parses
	a string of characters (call it a shape) input to it, looks up each character and draws it on the screen
	'''
	def __init__(self,turtlename,shapefile,start=[4,4],background = [69,86,255]):
		'''
		Constructor
		turtlename is the name of the turtle to control
		shapefile is the filename for the shape dictionary
		start is the starting position
		background is the background color of the turtlesim frame
		'''
		self.name = turtlename
		#publisher for turtle's cmd_vel
		self.publisher = rospy.Publisher('/%s/cmd_vel' % turtlename, geometry_msgs.msg.Twist,queue_size=2)
		#the shape dictionary with instructions to draw each shape
		self.shapes = pickle.load(open(shapefile, 'rb'))
		#the starting point for a new set of shapes
		self.start_x,self.start_y = start
		#the background color (so we can lift the pen)
		self.bg_r,self.bg_g,self.bg_b = background
		#convenience functions to call the teleport, setpen, and clear functions for turtlesim
		self.move_to_start = rospy.ServiceProxy(self.name+'/teleport_absolute', turtlesim.srv.TeleportAbsolute)
		self.clear_bg = rospy.ServiceProxy('clear', std_srvs.srv.Empty)
		self.set_pen = rospy.ServiceProxy(self.name+'/set_pen', turtlesim.srv.SetPen)
		
	def draw(self,shape):
		'''
		Publishes to cmd_vel of its turtle to draw each character in the shape, which is a string.
		These characters are encoded as lists of [linear, angular] velocity pairs.
		The artist adjusts the turtle once per second to draw the numbers.
		Between each character, the artist moves horizontally to a new space.
		In this particular dictionary, if there was an error, it will draw infinity.
		'''
		#teleport to start and clear screen
		rospy.wait_for_service(self.name+'/teleport_absolute')
		self.move_to_start(self.start_x, self.start_y, 0)
		rospy.wait_for_service('clear')
		#call the clear function
		self.clear_bg()
		#draw each shape in the string using the dictionary
		for char in shape:
			#for each shape, get the path
			path  = self.shapes[char]
			#publish the encoded velocities for each segment of the shape
			for p in path:
				publishVel(p[0],p[1],self.publisher)
				rospy.sleep(1)
			#lift the pen and move to start the next shape, if any
			rospy.wait_for_service(self.name+'/set_pen')
			self.set_pen(self.bg_r,self.bg_g,self.bg_b,0,0)
			publishVel(6,0,self.publisher)
			rospy.sleep(1)
			rospy.wait_for_service(self.name+'/set_pen')
			self.set_pen(255,255,255,0,0)


class Calculator:
	'''
	Stores the current command and waits for "equals" to evaluate.
	Has an instance of the Artist class which draws the result 
	'''
	def __init__(self,turtlename,charfile):
		self.command = ''
		#the numbers come in as strings, so map them to numbers
		self.numbers = {"ZERO": "0",
						"ONE": "1",
						"TWO": "2",
						"THREE": "3",
						"FOUR": "4",
						"FIVE": "5",
						"SIX": "6",
						"SEVEN": "7",
						"EIGHT": "8",
						"NINE": "9",
						"PLUS": "+",
						"MINUS": "-",
						"TIMES": "*"
						}
		#spin up an artist to draw what we calculate
		self.artist = Artist(turtlename,charfile)
		self.get_cmd = rospy.ServiceProxy('get_last_speech_cmd', SpeechService)
	def handle_input(self,msg):
		'''
		callback for new commands; appends to the current command and, if terminated,
		evaluates and draws output
		'''
		#call the listener service to get any commands in the queue
		rospy.wait_for_service('get_last_speech_cmd')
		cmd = []
		#get the command strings
		try:
			cmd = self.get_cmd().speech_cmd.split()
		except rospy.ServiceException, e:
			print "no command to get"
		#add each word's associated symbol to the current commmand unless equals, then eval
		for word in cmd:
			print word
			if word == 'EQUALS':
				self.calculate()
			else:
				try:
					self.command += self.numbers[word]
				except:
					pass #this should never happen if dict setup, but if not a valid input, ignore
	def calculate(self):
		'''
		Simply evaluate the string--if there's an error, indicate in the output.
		Send the result to the artist to draw
		'''
		try:
			#try evaluating
			answer = str(eval(self.command))
		except:
			answer = "ee" #err is a special shape in the dict (infinity)
		#draw and reset the current command
		self.artist.draw(answer)
		self.command = ''

if __name__ == '__main__':
	rospy.init_node('artist')
	turtlename = rospy.get_param('~turtlename')
	pwd = os.path.dirname(__file__)
	calc = Calculator(turtlename,os.path.join(pwd,"numbers.pkl"))
	#when the speech recognizer publishes an output, run a callback that calls the speech command service
	rospy.Subscriber('/hlpr_speech_commands', StampedString, calc.handle_input)
	rospy.spin()