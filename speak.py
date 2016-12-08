import pyttsx
import time

engine = pyttsx.init()
engine.say('Hello, my name is Baxter. Would you like to play a game?')

def gamespeak(name,completed):
	if completed:
		time.sleep(2)
		engine.say('Rock, Paper, Scissor, Shoot')

engine.connect('finished-utterance', gamespeak)

while(True):
	#time.sleep(5)
#	engine.runAndWait()
	engine.startLoop()
