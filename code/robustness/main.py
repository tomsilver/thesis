from experiment import Experiment
from util import plotResults

import players

def individualStrategies():
	#allxVals = {1: range(4, 10, 5), 2: range(100, 111, 10)}
	allxVals = {1: range(4, 101, 5), 2: range(100, 1001, 10)}
	allPlayerTypes = {'Random Play': players.RandomPlayer, 
					  'Honest Play': players.HonestPlayer, 
					  'Minimum Guessing': players.MinimumGuessingPlayer, 
					  'Constant Guessing': players.ConstantGuessPlayer, 
					  'Mean Guessing': players.MeanGuessPlayer, 
					  'Quantile Guessing': players.QuantileGuessPlayer,
					 }
	
	allExperimentTypes = [2]
	allStatistics = [2]

	for statistic in allStatistics:
		for experimentType in allExperimentTypes:
			xVals = allxVals[experimentType]
			for title, playerType in allPlayerTypes.items():
				playerTypes = {playerType: 1.0}
				savefile = title.replace(' ', '_')+str(experimentType)+str(statistic)+'.png'
				print "Running "+savefile

				exp = Experiment(xVals, playerTypes, experimentType, statistic)
				yVals = exp.run()
				print yVals
				plotResults(exp, yVals, title, savefile)
				print

def quantileStrategy():
	xVals = [10]
	playerTypes = {players.QuantileGuessPlayer: 1.0}
	experimentType = 2
	statistic = 1
	title = "Quantile Guessing"

	exp = Experiment(xVals, playerTypes, experimentType, statistic)
	yVals = exp.run()
	print yVals


if __name__ == '__main__':
	individualStrategies()
	#quantileStrategy()