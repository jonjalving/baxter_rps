from maestro import Controller
import time


class dummyController:
    def __init__(self):
        print "started dummy controller"
    def setTarget(self,channel,target):
        print "setting target for channel"+str(channel)+" to "+str(target)
    def close(self):
        print "closing dummy controller"

class RPS:
    def __init__(self, port='dummy'):
        #define some targets
        self.OPEN = 8000
        self.CLOSED = 5000
        self.port = port
        self.open_controller(self.port)
        #straighten all the fingers
        self.paper()
        
        #make a fist
        self.rock()
    def rock(self,delay=0.5):
        #make a fist
        self.rps_controller.setTarget(0,self.CLOSED)
        self.rps_controller.setTarget(1,self.CLOSED)
        self.rps_controller.setTarget(2,self.CLOSED-2000)
        time.sleep(delay)
    def paper(self,delay=0.5):
        #make an open palm
        self.rps_controller.setTarget(0,self.OPEN)
        self.rps_controller.setTarget(1,self.OPEN)
        self.rps_controller.setTarget(2,self.OPEN)
        time.sleep(delay)
    def scissors(self,delay=0.5):
        #make scissors
        self.rps_controller.setTarget(0,self.OPEN)
        self.rps_controller.setTarget(1,self.OPEN)
        self.rps_controller.setTarget(2,self.CLOSED-200)
        time.sleep(delay)
    def open_controller(self,port):
        if port=="dummy":
            self.rps_controller = dummyController()
        else:
            self.rps_controller = Controller(ttyStr=port)
    def close_controller(self):
        self.rps_controller.close()

if __name__ == "__main__":
    rps = RPS()
    rps.paper()
    rps.close_controller()
