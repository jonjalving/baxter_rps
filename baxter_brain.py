#!/usr/bin/env python  
import rospy


from std_msgs.msg import String
from hlpr_speech_msgs.msg import StampedString
#from hlpr_speech_msgs.srv import SpeechService
import speech_listener

import std_msgs.msg
import pickle
import numpy as np
import os

from bayes_filter import bayes_filter
#from decision_module import decision_module
from rps import RPS
import numpy as np

import logging

logger = logging.getLogger('__name__')
hdlr = logging.FileHandler('/home/cs4752/ros_ws/src/baxter_rps/baxter_brain.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.INFO)
logger.info("######################################################################")
class Baxter_RPS:
	def __init__(self,strategy):
		self.listening_flag = False
		self.watching_flag = False
		self.playing_flag = True
		self.rps = RPS(port='/dev/ttyACM0')
		#self.rps = RPS(port='dummy')
		self.counter = 0
		self.game_counter = 0
		self.last_state = ""
		self.strategy = strategy
		self.last_outcome = ""
		self.start_interval = 0
		self.belief_model = bayes_filter(["happy","meh","frustrated","quit"],np.array([1,0,0,0]))
		self.quit_threshold = 0.17
		self.detect_window_max = 5
		self.detect_counter = 0
		self.start_time = time.time()
	def handle_input(self,msg):
		if not self.listening_flag:
			return
		heard_phrase = msg.keyphrase
		if(heard_phrase == "YES"):
			self.interval = time.time()-self.start_interval
			print self.interval
			if(self.game_counter > 0):
				self.belief_model.evidence_update(self.interval)
			#log the interval
			self.game_counter += 1
			time.sleep(0.25)
			speak("OK")
			time.sleep(0.75)
			speak("Rock, Paper, Scissors")
			#time.sleep(0.01) #delay 10ms to get latest from camera
			#self.watching_flag = True
			self.speak_thoughtfully("Shoot")
			#while(not self.last_outcome):
			#	time.sleep(0.01)
			time.sleep(1)
			#speak(self.color_commentary())
			speak("Good game!")
			logger.info("Game number: "+str(self.game_counter)+", Result: "+self.last_outcome+", delay: "+str(self.interval))
		else:
			print "heard no"
			now = time.time()
			logger.info("Ending game at "+str(now)+ " Delay before NO was: "+str(now - self.start_interval)+" Total game time was: "+str(now-self.start_time))
			self.playing_flag = False
		self.listening_flag = False
		return
	def color_commentary(self):
		if(self.last_outcome == "win"):
			return "I won."
		elif(self.last_outcome == "lose"):
			return "You won."
		else:
			return "we tied"
	def hand_callback(self,msg):
		D = 0.001
		self.counter += 1
		#print str(self.counter)+":"+msg.data
		
		if not self.watching_flag:# or msg.data == self.last_state:
			return
		self.last_state = msg.data
		self.last_outcome = self.play(msg.data)

	def play(self,opponent_gesture):
		
		self.detect_counter += 1
		gestures = {"rock":{"win": self.rps.paper,"lose":self.rps.scissors,"tie":self.rps.rock},
					"paper":{"win":self.rps.scissors,"lose":self.rps.rock,"tie":self.rps.paper},
					"scissors":{"win":self.rps.rock,"lose":self.rps.paper,"tie":self.rps.scissors}
					}
		strategies = ["win","tie","lose"]
		#belief = [0,0,0,0] #BADDDDDNESSSS
		if self.strategy == "win":
			strategy = self.strategy
			belief = self.belief_model.action_check(strategy)
			
		elif self.strategy == "random":
			
			strategy = strategies[np.random.randint(len(strategies))]
			belief = self.belief_model.action_check(strategy)
		else:
			#adaptive model
			belief = np.ones(4)
			i = 0
			while belief[-1] > self.quit_threshold-(0*i) and i < len(strategies):
				belief = self.belief_model.action_check(strategies[i])
				i += 1

			strategy = strategies[i-1]
			#don't need to check for belief value b/c already done
		gestures[opponent_gesture][strategy]()
		if self.detect_counter >= self.detect_window_max:
			self.belief_model.action_update(belief)
			self.watching_flag = False
			self.detect_counter = 0
			print opponent_gesture
			return strategy
		return False

	def game_loop(self):
		self.start_time = self.start_interval
		while(self.playing_flag):
			time.sleep(0.005)
			if self.game_counter > 0:
				time.sleep(1)
				speak("Would you like to play again?")
				self.start_interval = time.time()
			self.listening_flag = True
			while(self.listening_flag):
				time.sleep(0.001)
			print "looping",self.playing_flag
		speak("ok, thanks for playing. goodbye")

	def speak_thoughtfully(self,*args):
		#https://answers.launchpad.net/python-espeak/+question/244655
	    done_synth = [False]
	    def cb(event, pos, length):
	        if event == espeak_core.event_MSG_TERMINATED:
	            done_synth[0] = True
	    espeak.set_SynthCallback(cb)
	    r = espeak.synth(*args)
	    count = 0
	    while r and not done_synth[0]:
	    	if count == 4:
	    		self.watching_flag = True
	    	count += 1
	        time.sleep(0.05)
	    return r




import time
from espeak import espeak
from espeak import core as espeak_core

def speak(*args):
	#https://answers.launchpad.net/python-espeak/+question/244655
    done_synth = [False]
    def cb(event, pos, length):
        if event == espeak_core.event_MSG_TERMINATED:
            done_synth[0] = True
    espeak.set_SynthCallback(cb)
    r = espeak.synth(*args)
    while r and not done_synth[0]:
        time.sleep(0.05)
    return r


if __name__ == '__main__':
	rospy.init_node('baxter_brain')
	mode = rospy.get_param('~mode')
	#pwd = os.path.dirname(__file__)
	#calc = Calculator(turtlename,os.path.join(pwd,"numbers.pkl"))
	#when the speech recognizer publishes an output, run a callback that calls the speech command service
	bgame = Baxter_RPS(mode)
	rospy.Subscriber('/hlpr_speech_commands', StampedString, bgame.handle_input)
	rospy.Subscriber('/user_hand',std_msgs.msg.String,bgame.hand_callback)
	speak("Hi,my name is Baxter, wanna play Rock Paper Scissors with me?")
	start_time = time.time()
	bgame.start_interval = start_time
	logger.info("Starting game at "+str(bgame.start_interval))
	bgame.game_loop()
	#rospy.spin()
	#load the probability models
	#create a bayes filter module with the probability models
	#create a decision model
	#create an rps object


	#workflow:
	#say welcome message
		#time.sleep(4)
	#loop:
	#Say, "would you like to play rock paper scissors?"
	#listen for response
	#if no, quit
	#if yes, strategy = decision_model.update_strategy() (looks at belief state and returns win, lose, or tie)
	#say "rock, paper, scissors, shoot"
	#call play function on rps object (turn the subscriber on for the camera for x seconds)
	#say "I win", "you win", or "tie game"
	#rospy.spin()
