from predictor import Predictor
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



class BOWRegression(ResponseBasedPredictor):

	def responseToVec(self, resp):
		words = util.wordsFromResponse(resp)
		v = np.zeros(self.vecDim, dtype=float)
		for word in words:
			if word in self.wordIndices:
				idx = self.wordIndices[word]
				v[idx] += 1
		return v



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



if __name__ == '__main__':
	ql = util.parseMohler()
	bow = NGramRegression(ql, 1)
	print bow.run()


						
