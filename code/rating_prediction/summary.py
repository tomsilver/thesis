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
	'twc': TrainedWord2VecCosine,
	'snl': LiSemanticNets,
	'bow': NGramRegression,
	'big': BigramRegression,
	'syn': BagOfSynsets,
	'nno': NearestNeighborOverlap,
	'nnc': NearestNeighborCharEditDistance,
	'nnw': NearestNeighborWordEditDistance
}


def getAllRMSES(dataParser, allPredictors, outfile=None):
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

	totalErrors = {k:[] for k in allPredictors}
	totalErrors['com'] = []

	# ignore random guess and constant best guess
	featPreds = [p for p in allPredictors.values() if p(None).canBeFeature()]

	for i in range(TRIALS):
		try:
			print "Trial", i
			ql = dataParser()

			for pid, predictor in allPredictors.items():
				predictorInstance = predictor(ql)
				predictorError = predictorInstance.run()
				totalErrors[pid].append(predictorError)
				print pid+" error for trial:",
				print predictorError

			combinedModel =	CombinedModel(ql, featPreds, universalRegression)
			combinedError = combinedModel.run()
			totalErrors['com'].append(combinedError)
			print "com error for trial:",
			print combinedError
			print
		except:
			print "FAILED; continuing"

	result_str = ''

	for k, err in totalErrors.items():
		mean_err = np.mean(totalErrors[k])
		std_err = np.std(totalErrors[k])
		totalErrors[k] = (mean_err, std_err)
		print k+" average RMSE:",
		print totalErrors[k][0],
		print "(std=",
		print totalErrors[k][1],
		print ")"
		result_str += k+','+str(totalErrors[k][0])+','+str(totalErrors[k][1])+'\n'

	if outfile is not None:
		with open(outfile, 'wb') as f:
			f.write(result_str)
			print "Wrote out results to"+outfile


	return totalErrors


def summaryPlot(allPredictors):

	powergradingRmses = getAllRMSES(parsePowerGrading, allPredictors, 'tmp/powergrade.txt')
	mohlerRmses = getAllRMSES(parseMohler, allPredictors, 'tmp/mohler.txt')

	plotOrder = ['ran', 'cbg', 'bwo', 'fwo', 'ced', 'wed', 'wcs', 'twc', 'snl', 'bow', 'big', 'syn', 'nno', 'nnc', 'nnw', 'com']
	thisPlotOrder = [x for x in plotOrder if x in allPredictors]+['com']

	# powergradingRmses = {
	# 	'nno': 0.104996565464,
	# 	'wcs': 0.303457071201,
	# 	'ced': 0.222430640695,
	# 	'cbg': 0.140711453358,
	# 	'wed': 0.292737911941,
	# 	'ran': 0.404844982315,
	# 	'big': 0.143233752466,
	# 	'nnc': 0.13078342523,
	# 	'syn': 0.145602936257,
	# 	'bow': 0.142364570248,
	# 	'fwo': 0.337321203787,
	# 	'nnw': 0.136372687701,
	# 	'com': 0.139330451839,
	# 	'bwo': 0.129107048882
	# }

	# mohlerRmses = {
	# 	'nno': 0.334043106828,
	# 	'wcs': 0.410271471806,
	# 	'ced': 0.404274748717,
	# 	'cbg': 0.31218166308,
	# 	'wed': 0.506789079935,
	# 	'ran': 0.423024410079,
	# 	'big': 0.313552257668,
	# 	'nnc': 0.319353207697,
	# 	'syn': 0.341390702405,
	# 	'bow': 0.316211663839,
	# 	'fwo': 0.571466711299,
	# 	'nnw': 0.313509694805,
	# 	'com': 0.328019353549,
	# 	'bwo': 0.311710847431
	# }

	N = len(allPredictors)+1
	strategies, prermses1 = zip(*[x for x in powergradingRmses.items()])
	rmses1 = [None for _ in prermses1]
	stds1 = [None for _ in prermses1]
	for i, s in enumerate(strategies):
		idx = thisPlotOrder.index(s)
		rmses1[idx] = prermses1[i][0]
		stds1[idx] = prermses1[i][1]

	ind = np.arange(N)  # the x locations for the groups
	width = 0.35       # the width of the bars

	fig, ax = plt.subplots()
	rects1 = ax.bar(ind, rmses1, width, color='r', yerr=stds1)

	strategies, prermses2 = zip(*[x for x in mohlerRmses.items()])
	rmses2 = [None for _ in prermses2]
	stds2 = [None for _ in prermses2]
	for i, s in enumerate(strategies):
		idx = thisPlotOrder.index(s)
		rmses2[idx] = prermses2[i][0]
		stds2[idx] = prermses2[i][1]
	rects2 = ax.bar(ind + width, rmses2, width, color='y', yerr=stds2)

	# add some text for labels, title and axes ticks
	ax.set_ylabel('RMSE')
	ax.set_title('Luna Rating Prediction with OLS Regressions')
	ax.set_xticks(ind + width)
	ax.set_xticklabels([s.upper() for s in thisPlotOrder])

	ax.legend((rects1[0], rects2[0]), ('Powergrading', 'Mohler 11'))

	locs, labels = plt.xticks()
	plt.setp(labels, rotation=30)

	plt.show()

if __name__ == '__main__':
	summaryPlot(allPredictors)