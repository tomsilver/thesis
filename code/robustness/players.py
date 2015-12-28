import numpy as np
import util


class Player(object):
	def __init__(self):
		self.smartsRating = None
		self.intelligence = None
		self.ratingUpdates = 0.0

	def getIntelligence(self):
		return self.intelligence

	def setIntelligence(self, v):
		self.intelligence = v

	def getSmartsRating(self):
		return self.smartsRating

	def setSmartsRating(self, v):
		self.smartsRating = v

	def updateSmartsRating(self, v):
		if self.smartsRating is None:
			self.setSmartsRating(v)
		else:
			N = self.ratingUpdates
			self.smartsRating = (N*self.smartsRating + v)/(N+1)
			self.ratingUpdates += 1

	def actualGuess(self, player):
		raise UnimplementedError

	def reportGuess(self, player):
		raise UnimplementedError

	def L1Error(self):
		return abs(self.getIntelligence() - self.getSmartsRating())

	def hasPlayed(self):
		return self.smartsRating is not None



class SimulatedPlayer(Player):
	def __init__(self, baselineRating, mu=0, sigma2=5.0):
		super(SimulatedPlayer, self).__init__()
		self.baselineRating = baselineRating
		self.actualGuesses = {} # dict of players to guesses
		self.mu = mu
		self.sigma2 = sigma2

	def getBaselineRating(self):
		return self.baselineRating

	def actualGuess(self, player):		
		if player not in self.actualGuesses:
			rating = player.getBaselineRating()
			guess = rating + np.random.normal(self.mu, self.sigma2)
			self.actualGuesses[player] = guess
		
		return self.actualGuesses[player]


class RandomPlayer(SimulatedPlayer):
	def __init__(self, baselineRating, mu=0, sigma2=5.0):
		super(RandomPlayer, self).__init__(baselineRating, mu, sigma2)
		self.reportedGuesses = {}

	def reportGuess(self, player, allPlayers):
		if player not in self.reportedGuesses:
			guess = 100*np.random.random()
			self.reportedGuesses[player] = guess
		
		return self.reportedGuesses[player]


class HonestPlayer(SimulatedPlayer):
	def reportGuess(self, player, allPlayers):
		return self.actualGuess(player)


class MinimumGuessingPlayer(SimulatedPlayer):
	def reportGuess(self, player, allPlayers):
		return 0


class ConstantGuessPlayer(SimulatedPlayer):
	def reportGuess(self, player, allPlayers):
		return 50


class MeanGuessPlayer(SimulatedPlayer):
	def reportGuess(self, player, allPlayers):
		report = util.meanSmartsRating(allPlayers)
		if report is None:
			report  = self.actualGuess(player)
		return report


class QuantileGuessPlayer(SimulatedPlayer):
	def reportGuess(self, player, allPlayers):
		guess = self.actualGuess(player)
		p = util.getQuantile(guess, self.actualGuesses.values())
		report = util.quantileFunction(p, allPlayers)
		if report is None:
			report = guess

		print "actual guess:", guess
		print "p = ", p
		print "reporting guess: ", report
		return report
