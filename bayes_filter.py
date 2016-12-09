import numpy as np
from scipy import stats
import logging

class bayes_filter:


	def __init__(self,states,initial_belief):
		self.logger = logging.getLogger('__name__')
		hdlr = logging.FileHandler('/home/cs4752/ros_ws/src/baxter_rps/baxter_bayes_filter.log')
		formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
		hdlr.setFormatter(formatter)
		self.logger.addHandler(hdlr) 
		self.logger.setLevel(logging.INFO)
		self.logger.info("######################################################################")
		self.actions = ["win","tie","lose"]
		self.states = states
		self.belief = initial_belief
		self.eps = 10e-4
		self.emission_probabilities = [stats.norm(1,1),stats.norm(2,1),stats.norm(4,1),stats.norm(6,4)]
		self.update_probabilities = np.array([[[0.4,0.5,0.09,0.01],	#win
												[0.05,0.6,0.3,0.05],
												[0.01,0.04,0.45,0.5],
												[0,0,0,1]],
											  [[0.7,0.25,0.04,0.01],	#tie
											  	[0.15,0.75,0.08,0.02],
											  	[0.01,0.09,0.65,0.25],
											  	[0,0,0,1]],
											  [[0.82,0.15,0.02,0.01],	#lose
											  	[0.6,0.35,0.03,0.02],
											  	[0.1,0.6,0.21,0.05],
											  	[0,0,0,1]]])
	def get_prob(self,x,distr):
		return distr.cdf(x+self.eps)-distr.cdf(x-self.eps)

	def action_check(self,action):
		action_index = self.actions.index(action)
		new_belief = np.zeros(len(self.belief))
		for i,belief_state in enumerate(new_belief):
			for j,prior_belief_state in enumerate(self.belief):
				belief_state += self.update_probabilities[action_index][j][i]*self.belief[j] #probabilites[this state][prior state][index]
			new_belief[i] = belief_state
		self.logger.info("Action Prediction for "+action+": "+str(new_belief))
		return new_belief 

	def action_update(self,new_belief):
		self.logger.info("Action Update: "+str(new_belief))
		self.belief = new_belief
	def evidence_update(self,evidence):
		eta = 0
		print self.belief
		print "interval: ",evidence
		new_belief = np.zeros(len(self.belief))
		for i,x in enumerate(self.belief):
			print self.get_prob(evidence,self.emission_probabilities[i])
			new_belief[i] = self.get_prob(evidence,self.emission_probabilities[i])*x
			eta += new_belief[i]
		new_belief[-1] = 0
		print "ETA::::",str(eta)
		print "normalized:",(1.0/eta)*new_belief
		self.belief = (1.0/eta)*new_belief
		self.logger.info("Evidence Update: "+str(self.belief))