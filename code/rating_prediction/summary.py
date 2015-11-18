from comprehensivePrediction import CombinedModel
from matplotlib import pyplot as plt
from questionBasedPrediction import *
from predictor import ConstantBestGuessPredictor, RandomPredictor
from responseBasedPrediction import *
from sklearn import linear_model
from util import parseMohler, parsePowerGrading, TRIALS, universalRegression

import numpy as np

allPredictors = {
	'ran': RandomPredictor,
	'cbg': ConstantBestGuessPredictor,
	'bwo': BinaryOverlapPredictor,
	'fwo': FractionOverlapPredictor,
	'ced': CharEditDistancePredictor,
	'wed': WordEditDistancePredictor,
	'wcs': Word2VecCosine,
	#'snl': LiSemanticNets,
	'bow': NGramRegression,
	'big': BigramRegression,
	'syn': BagOfSynsets,
	'nno': NearestNeighborOverlap,
	'nnc': NearestNeighborCharEditDistance,
	'nnw': NearestNeighborWordEditDistance,
}


def getAllRMSES(dataParser, allPredictors):
	"""List of all:
	-random guesses (ran)
	-constant best guess (cbg)
	-binary word overlap (bwo)
	-fraction word overlap (fwo)
	-character edit distance (ced)
	-word edit distance (wed)
	-word2vec cosine similarity (wcs)
	-semantic nets (snl)
	-bag of words (bow)
	-bigrams (big)
	-bag of synsets (syn)
	-nearest neighbor overlap (nno)
	-nearest neighbor via ced (nnc)
	-nearest neighbor via wed (nnw)
	-combination of all (com)

	"""

	totalErrors = {k:0.0 for k in allPredictors}
	totalErrors['com'] = 0.0

	# ignore random guess and constant best guess
	featPreds = [p for p in allPredictors.values() if p(None).canBeFeature()]

	for i in range(TRIALS):
		print "Trial", i
		ql = dataParser()

		for pid, predictor in allPredictors.items():
			predictorInstance = predictor(ql)
			predictorError = predictorInstance.run()
			totalErrors[pid] += predictorError
			print pid+" error for trial:",
			print predictorError

		combinedModel =	CombinedModel(ql, featPreds, universalRegression)
		combinedError = combinedModel.run()
		totalErrors['com'] += combinedError
		print "com error for trial:",
		print combinedError
		print

	for k, err in totalErrors.items():
		totalErrors[k] = err/TRIALS
		print k+" average RMSE:"
		print totalErrors[k]

	return totalErrors


def summaryPlot(allPredictors):

	powergradingRmses = getAllRMSES(parsePowerGrading, allPredictors)
	mohlerRmses = getAllRMSES(parseMohler, allPredictors)

	# powergrading_rmses = [0.426311174463,0.161877949651,0.12963277378,0.125467131023,0.134417628097,0.159157051495,0.733231595034,0.150405027703,0.154884567719]
	# mohler_rmses = [0.444748784415,0.303005941018,0.312529802318,0.32777232683,0.323964540167,0.386071354774,0.272206377857,0.322195377856,0.31867538719]

	N = len(allPredictors)
	strategies = allPredictors.keys()
	rmses1 = powergradingRmses

	ind = np.arange(N)  # the x locations for the groups
	width = 0.35       # the width of the bars

	fig, ax = plt.subplots()
	rects1 = ax.bar(ind, rmses1, width, color='r', yerr=None)

	rmses2 = mohlerRmses
	rects2 = ax.bar(ind + width, rmses2, width, color='y', yerr=None)

	# add some text for labels, title and axes ticks
	ax.set_ylabel('RMSE')
	ax.set_title('Rating Prediction Results')
	ax.set_xticks(ind + width)
	ax.set_xticklabels(strategies)

	ax.legend((rects1[0], rects2[0]), ('Powergrading', 'Mohler 11'))

	locs, labels = plt.xticks()
	plt.setp(labels, rotation=30)

	plt.show()

if __name__ == '__main__':
	summaryPlot(allPredictors)