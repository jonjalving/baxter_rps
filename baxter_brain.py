#!/usr/bin/env python  
import rospy


from std_msgs.msg import String
from hlpr_speech_msgs.msg import StampedString
from hlpr_speech_msgs.srv import SpeechService
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

class Baxter_RPS:
	def __init__(self,strategy):
		self.listening_flag = False
		self.watching_flag = False
		self.playing_flag = True
		#self.rps = RPS(port='/dev/ttyACM0')
		self.rps = RPS(port='dummy')
		self.counter = 0
		self.game_counter = 0
		self.last_state = ""
		self.strategy = strategy
		self.last_outcome = ""
		self.start_interval = 0
	def handle_input(self,msg):
		if not self.listening_flag:
			return
		heard_phrase = msg.keyphrase
		if(heard_phrase == "YES"):
			self.interval = time.time()-self.start_interval
			#log the interval
			self.game_counter += 1
			speak("Rock, Paper, Scissors,")
			self.watching_flag = True
			speak("Shoot")
			time.sleep(2)
			speak(self.color_commentary())
		else:
			print "heard no"
			self.playing_flag = False
		self.listening_flag = False
		return
	def color_commentary(self):
		if(self.last_outcome == "win"):
			return "Oh Yeah! I won, I won, I won!"
		elif(self.last_outcome == "lose"):
			return "You son of a bitch. You won that round."
		else:
			return "looks like we tied"
	def hand_callback(self,msg):
		D = 0.001
		self.counter += 1
		#print str(self.counter)+":"+msg.data
		
		if not self.watching_flag:# or msg.data == self.last_state:
			return
		self.last_state = msg.data
		self.last_outcome = self.play(msg.data)

	def play(self,opponent_gesture):
		
		gestures = {"rock":{"win": self.rps.paper,"lose":self.rps.scissors,"tie":self.rps.rock},
					"paper":{"win":self.rps.scissors,"lose":self.rps.rock,"tie":self.rps.paper},
					"scissors":{"win":self.rps.rock,"lose":self.rps.paper,"tie":self.rps.scissors}
					}
		
		if self.strategy == "win":
			strategy = self.strategy
			
		elif self.strategy == "random":
			strategies = ["win","lose","tie"]
			strategy = strategies[np.random.randint(len(strategies))]
		else:
			#adaptive model
			strategy = "lose"
		gestures[opponent_gesture][strategy]()
		self.watching_flag = False
		return strategy

	def game_loop(self):
		while(self.playing_flag):
			time.sleep(0.005)
			if self.game_counter > 0:
				time.sleep(1)
				speak("Would you like to play again?")
				self.start_interval = time.time()
			self.listening_flag = True
			while(self.listening_flag):
				time.sleep(0.005)
			print "looping",self.playing_flag
		speak("ok, thanks for playing. goodbye")



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
        time.sleep(0.005)
    return r

if __name__ == '__main__':
	rospy.init_node('baxter_brain')

	#pwd = os.path.dirname(__file__)
	#calc = Calculator(turtlename,os.path.join(pwd,"numbers.pkl"))
	#when the speech recognizer publishes an output, run a callback that calls the speech command service
	bgame = Baxter_RPS("random")
	rospy.Subscriber('/hlpr_speech_commands', StampedString, bgame.handle_input)
	rospy.Subscriber('/user_hand',std_msgs.msg.String,bgame.hand_callback)
	speak("Hi, I'm Baxter. Would you like to play Rock, Paper, Scissors with me?")
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