from rps import RPS
import rospy
import std_msgs.msg
rps = RPS(port='/dev/ttyACM0')
counter = 0
last_state = ""
def rock_callback():
    rps.rock()

def paper_callback():
    rps.paper()

def scissors_callback():
    rps.scissors()

def hand_callback(msg):
	global counter,last_state
	D = 0.001
	counter += 1
	print str(counter)+":"+msg.data
	if msg.data == last_state:
		return
	last_state = msg.data
	if msg.data == "rock":
		print "got rock, playing paper\n"
		rps.paper(delay=D)
	elif msg.data == "paper":
		print "got paper, playing scissors\n"
		rps.scissors(delay=D)
	elif msg.data == "scissors":
		print "got scissors, playing rock\n"
		rps.rock(delay=D)

if __name__ == '__main__':
	
	rospy.init_node('baxter_hand')
	rospy.Subscriber('/user_hand',std_msgs.msg.String,hand_callback)
	rps.scissors()
	rospy.spin()