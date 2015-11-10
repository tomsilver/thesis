from predictor import ConstantBestGuessPredictor, Predictor, RandomPredictor
from sklearn import linear_model

import numpy as np
import util


class QBRegression(Predictor):

	def compareWithIdeal(self, response, ideals):
		raise UnimplementedError

	def train(self, X, y):
		self.lr = linear_model.Lasso()
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



if __name__ == '__main__':
	total_err_ran = 0.0
	total_err_cbg = 0.0
	total_err_bop = 0.0
	total_err_fop = 0.0

	for i in range(util.TRIALS):
		print "Trial", i

		ql = util.parsePowerGrading()
		ran = RandomPredictor(ql)
		cbg = ConstantBestGuessPredictor(ql)
		bop = BOPRegression(ql)
		fop = FOPRegression(ql)

		total_err_ran += ran.run()
		total_err_cbg += cbg.run()
		total_err_bop += bop.run()
		total_err_fop += fop.run()

	print "Average Random RMSE:",
	print total_err_ran/util.TRIALS

	print "Average CBG RMSE:",
	print total_err_cbg/util.TRIALS

	print "Average BOP RMSE:",
	print total_err_bop/util.TRIALS

	print "Average FOP RMSE:",
	print total_err_fop/util.TRIALS
