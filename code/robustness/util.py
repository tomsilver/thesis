from matplotlib import pyplot as plt
from statsmodels.distributions.empirical_distribution import ECDF

import numpy as np
import os


def playersToRatings(players):
	return [p.getSmartsRating() for p in players if p.hasPlayed()]

def calculateIntelligences(players):
	N = 1.0*len(players)
	for p in players:
		Ip = 0.0
		for o in players:
			Ip += o.actualGuess(p)
		p.setIntelligence(Ip/N)

def meanSmartsRating(players):
	ratings = playersToRatings(players)
	if len(ratings) == 0:
		return None
	return np.mean(ratings)

def getQuantile(guess, sample):
	if len(sample) == 0:
		return 0.5
	ecdf = ECDF(sample)
	return ecdf(guess)

def quantileFunction(p, allPlayers):
	ratings = playersToRatings(allPlayers)
	if len(ratings) == 0:
		return None
	return np.percentile(ratings, p)

def plotResults(e, yVals, title, savefile=None):
	
	xVals = e.xVals
	experimentType = e.experimentType
	statistic = e.statistic

	plt.figure()

	if experimentType == 1:
		plt.xlabel("Population Size")
		titleSup = " (T="+str(e.defaultT)+")"
	elif experimentType == 2:
		plt.xlabel("Time Steps")
		titleSup = " (N="+str(e.defaultN)+")"

	if statistic == 1:
		plt.ylabel("Mean L1 Error")
	elif statistic == 2:
		plt.ylabel("Max L1 Error")

	plt.title(title+titleSup)
	plt.plot(xVals, yVals)
	
	if savefile is None:
		plt.show()
	else:
		filePath = os.path.join('../../figures', 'robustness', savefile)
		with open(filePath, 'wb') as f:
			plt.savefig(f)
		print "saved to "+str(savefile)