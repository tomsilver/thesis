from questionBasedPrediction import BinaryOverlapPredictor, CharEditDistancePredictor, FractionOverlapPredictor, WordEditDistancePredictor
from predictor import ConstantBestGuessPredictor, Predictor, RandomPredictor
from responseBasedPrediction import BigramRegression, NGramRegression, TrigramRegression

import numpy as np
import util


class QBRegression(Predictor):

	def compareWithIdeal(self, response, ideals):
		raise UnimplementedError

	def train(self, X, y):
		self.lr = util.universalRegression()
		self.lr.fit(X, y)

	def predict(self, X):
		return self.lr.predict(X)

	def parseQuestionList(self, questionList):

		qpr = questionList.getQuestionsPerRespondent()

		X = []
		y = []

		for respondent, responses in qpr.items():
			x = []
			for resp in responses:
				ideal = resp.getIdeal()
				x.append(self.compareWithIdeal(resp, ideal))

			X.append(x)
			y.append(respondent.getRating())

		return X, y



class BOPRegression(QBRegression):

	def compareWithIdeal(self, response, ideals):
		for ideal in ideals:
			for word in response.split():
				if word in ideal:
					return 1.0
		return 0.0



class FOPRegression(QBRegression):

	def compareWithIdeal(self, response, ideals):
		max_overlap = 0
		for ideal in ideals:
			N = 1.0*len(ideal)
			this_overlap = 0
			for word in response.split():
				if word in ideal:
					this_overlap += 1
			max_overlap = max(max_overlap, this_overlap/N)

		return max_overlap



class CombinedModel(Predictor):
	def __init__(self, questionList, featurePredictors, topLevelPredictor):
		self.questionList = questionList
		self.featurePredictorModels = featurePredictors
		self.topLevelPredictorModel = topLevelPredictor
		super(CombinedModel, self).__init__(questionList)

	def prepare(self, train):
		self.topLevelPredictor = self.topLevelPredictorModel()
		self.featurePredictors = []
		for featurePredictor in self.featurePredictorModels:
			fp = featurePredictor(self.questionList)
			fp.prepare(train)
			self.featurePredictors.append(fp)

	def train(self, X, y):
		try:
			self.topLevelPredictor.train(X, y)
		except AttributeError:
			self.topLevelPredictor.fit(X, y)

	def predict(self, X):
		return self.topLevelPredictor.predict(X)

	def parseQuestionList(self, questionList):
		qpr = questionList.getQuestionsPerRespondent()

		X = []
		y = []

		for featurePredictor in self.featurePredictors:
			if len(X) == 0:
				X, y = featurePredictor.parseQuestionList(questionList)
			else:
				thisX, _ = featurePredictor.parseQuestionList(questionList)
				for i, entry in enumerate(X):
					X[i] = np.concatenate((entry, thisX[i]))

		return X, y





if __name__ == '__main__':
	total_err_ran = 0.0
	total_err_cbg = 0.0
	total_err_bop = 0.0
	total_err_fop = 0.0
	total_err_edit = 0.0
	total_err_cep = 0.0
	total_err_com = 0.0

	for i in range(util.TRIALS):
		print "Trial", i

		ql = util.parsePowerGrading()
		ran = RandomPredictor(ql)
		cbg = ConstantBestGuessPredictor(ql)
		bop = BOPRegression(ql)
		fop = FOPRegression(ql)
		cep = CharEditDistancePredictor(ql)
		edit = WordEditDistancePredictor(ql)
		com = CombinedModel(ql, [NGramRegression, FractionOverlapPredictor, CharEditDistancePredictor], linear_model.LinearRegression)

		total_err_ran += ran.run()
		total_err_cbg += cbg.run()
		total_err_bop += bop.run()
		total_err_fop += fop.run()
		total_err_edit += edit.run()
		total_err_cep += cep.run()
		total_err_com += com.run()

	print "Average Random RMSE:",
	print total_err_ran/util.TRIALS

	print "Average CBG RMSE:",
	print total_err_cbg/util.TRIALS

	print "Average BOP RMSE:",
	print total_err_bop/util.TRIALS

	print "Average FOP RMSE:",
	print total_err_fop/util.TRIALS

	print "Average Char Edit RMSE:",
	print total_err_cep/util.TRIALS

	print "Average Word Edit RMSE:",
	print total_err_edit/util.TRIALS

	print "Average COM RMSE:",
	print total_err_com/util.TRIALS
