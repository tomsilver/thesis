import numpy as np
import players
import random
import util


class Experiment(object):
	def __init__(self, 
				 xVals, 
				 playerTypeDict, 
				 experimentType,
				 statistic, 
				 defaultN=100, 
				 defaultT=1000,
				 minSR=0,
				 maxSR=100,
				 repeats=50):
		self.xVals = xVals # a list of population sizes or time lengths
		self.playerTypeDict = playerTypeDict # SimulatedPlayers to population fracs
		self.experimentType = experimentType # 1 = T fixed, 2 = N fixed
		self.statistic = statistic # 1 = average, 2 = max
		self.defaultN = defaultN
		self.defaultT = defaultT
		self.minSR = minSR
		self.maxSR = maxSR
		self.repeats = repeats
		self.allPlayers = []

		assert self.statistic == 1 or self.statistic == 2
		assert self.experimentType == 1 or self.experimentType == 2
		assert sum(self.playerTypeDict.values()) == 1.0

	def generatePlayers(self, N):
		players = []
		for playerType, freq in self.playerTypeDict.items():
			playerCount = int(freq*N)
			for _ in range(playerCount):
				baseline = random.random()*(self.maxSR-self.minSR)+self.minSR
				newPlayer = playerType(baseline)
				players.append(newPlayer)

		util.calculateIntelligences(players)
		self.allPlayers = players
		return players

	def runSingleMatch(self, player1, player2):
		player1Guess = player1.reportGuess(player2, self.allPlayers)
		player2Guess = player2.reportGuess(player1, self.allPlayers)
		player1.updateSmartsRating(player2Guess)
		player2.updateSmartsRating(player1Guess)

	def runMatches(self, players, T):
		for t in range(T):
			player1, player2 = random.sample(players, 2)
			self.runSingleMatch(player1, player2)

	def calculateErrors(self, players):
		errors = [p.L1Error() for p in players if p.hasPlayed()]
		if self.statistic == 1:
			return np.mean(errors)
		elif self.statistic == 2:
			return np.max(errors)
		raise("Invalid statistic "+str(statistic))

	def runSingleExperiment(self, N, T):
		print "Running experiment N="+str(N)+", T="+str(T)
		meanError = 0.0
		for _ in range(self.repeats):
			players = self.generatePlayers(N)
			self.runMatches(players, T)
		 	meanError += np.array(self.calculateErrors(players))
		return meanError/self.repeats

	def runPopulationExperiment(self):
		yVals = []
		for N in self.xVals:
			yVals.append(self.runSingleExperiment(N, self.defaultT))
		return yVals

	def runTimeExperiment(self):
		yVals = []
		for T in self.xVals:
			yVals.append(self.runSingleExperiment(self.defaultN, T))
		return yVals

	def run(self):
		if self.experimentType == 1:
			yVals = self.runPopulationExperiment()
		elif self.experimentType == 2:
			yVals = self.runTimeExperiment()
		else:
			raise("Invalid experiment type "+str(self.experimentType))

		return yVals
