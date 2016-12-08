import numpy as np

class bayes_filter:
	def __init__(self,states,initial_belief):
		self.states = states
		self.belief = initial_belief
		self.update_probabilities
		self.emission_probabilities

	def action_predict(self,action_index):
		new_belief = np.array(len(self.belief))
		for i,belief_state in enumerate(new_belief):
			for j,prior_belief_state in enumerate(self.belief):
				belief_state += self.update_probabilities[i][j][action_index] #probabilites[this state][prior state][index]
		return new_belief 

	def evidence_update(self,evidence):
		eta = 0
		new_belief = np.array(len(self.belief))
		for i,x in enumerate(self.belief):
			new_belief[i] = self.emission_probabilities[i]
