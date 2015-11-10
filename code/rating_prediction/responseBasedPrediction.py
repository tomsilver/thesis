from predictor import ConstantBestGuessPredictor, Predictor, RandomPredictor
from sklearn import linear_model

import numpy as np
import util


class ResponseBasedPredictor(Predictor):

	def prepare(self, train):
		all_words = list(util.wordsFromQuestionList(train))
		self.wordIndices = {}
		for idx, word in enumerate(all_words):
			self.wordIndices[word] = idx
		self.vecDim = len(all_words)

	def train(self, X, y):
		self.lr = linear_model.LinearRegression()
		self.lr.fit(X, y)

	def predict(self, X):
		return self.lr.predict(X)

	def responseToVec(self, resp):
		"""Returns a numpy array. Needs to be implemented by subclass."""
		raise UnimplementedError

	def parseQuestionList(self, questionList):
		"""Sum all question vectors."""
		qpr = questionList.getQuestionsPerRespondent()

		X = []
		y = []

		for respondent, responses in qpr.items():
			x = None
			for resp in responses:
				v = self.responseToVec(resp)
				if x is None:
					x = v
				else:
					x += v

			X.append(x)
			y.append(respondent.getRating())

		return X, y



class IndividualResponseBasedPredictor(ResponseBasedPredictor):

	def parseQuestionList(self, questionList):
		"""Maintain all question vectors."""
		qpr = questionList.getQuestionsPerRespondent()

		X = []
		y = []

		for respondent, responses in qpr.items():
			x = []
			for resp in responses:
				x.extend(self.responseToVec(resp))

			X.append(x)
			y.append(respondent.getRating())

		return X, y



class NGramRegression(ResponseBasedPredictor):

	def __init__(self, questionList, ngram_cap=2):
		super(NGramRegression, self).__init__(questionList)
		self.ngram_cap = ngram_cap

	def prepare(self, train):
		all_words = list(util.wordsFromQuestionList(train, self.ngram_cap))
		self.wordIndices = {}
		for idx, word in enumerate(all_words):
			self.wordIndices[word] = idx
		self.vecDim = len(all_words)

	def responseToVec(self, resp):
		words = set()
		for ngram in range(1, self.ngram_cap+1):
			words |= util.wordsFromResponse(resp, ngram)

		v = np.zeros(self.vecDim, dtype=float)
		for word in words:
			if word in self.wordIndices:
				idx = self.wordIndices[word]
				v[idx] += 1
		return v


class IndividualNGramRegression(IndividualResponseBasedPredictor):

	def __init__(self, questionList, ngram_cap=2):
		super(IndividualNGramRegression, self).__init__(questionList)
		self.ngram_cap = ngram_cap

	def prepare(self, train):
		all_words = list(util.wordsFromQuestionList(train, self.ngram_cap))
		self.wordIndices = {}
		for idx, word in enumerate(all_words):
			self.wordIndices[word] = idx
		self.vecDim = len(all_words)

	def responseToVec(self, resp):
		words = set()
		for ngram in range(1, self.ngram_cap+1):
			words |= util.wordsFromResponse(resp, ngram)

		v = np.zeros(self.vecDim, dtype=float)
		for word in words:
			if word in self.wordIndices:
				idx = self.wordIndices[word]
				v[idx] += 1
		return v



if __name__ == '__main__':
	total_err_ran = 0.0
	total_err = 0.0
	total_err1 = 0.0
	total_err2 = 0.0
	total_err3 = 0.0

	for i in range(util.TRIALS):
		print "Trial", i

		ql = util.parsePowerGrading()
		ran = RandomPredictor(ql)
		bow = ConstantBestGuessPredictor(ql)
		bow1 = NGramRegression(ql, 1)
		bow2 = NGramRegression(ql, 2)
		bow3 = NGramRegression(ql, 3)
		total_err_ran += ran.run()
		total_err += bow.run()
		total_err1 += bow1.run()
		total_err2 += bow2.run()
		total_err3 += bow3.run()

	print "Average Random RMSE:",
	print total_err_ran/util.TRIALS

	print "Average CBG RMSE:",
	print total_err/util.TRIALS

	print "Ngram 1 Average RMSE:",
	print total_err1/util.TRIALS

	print "Ngram 2 Average RMSE:",
	print total_err2/util.TRIALS

	print "Ngram 3 Average RMSE:",
	print total_err3/util.TRIALS


						
