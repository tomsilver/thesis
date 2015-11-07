from questions import QuestionList
from sklearn import linear_model

import numpy as np
import util


class RatingRegression(object):

	def __init__(self, questionList):
		self.questionList = questionList

	def run(self):
		train, test = util.splitData(self.questionList.questions)
		self.prepare(train)

		trainX, trainy = self.parseQuestionList(QuestionList(train))
		testX, testy = self.parseQuestionList(QuestionList(test))
		self.train(trainX, trainy)
		preds = self.predict(testX)
		return self.evaluate(preds, np.array(testy))

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
		if not hasattr(self, 'lr'):
			raise("Trying to predict without any prior training.")

		return self.lr.predict(X)

	def evaluate(self, preds, testy):
		rmse = np.sqrt(np.mean(np.square(preds-testy)))
		return rmse

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



class BOWRegression(RatingRegression):

	def responseToVec(self, resp):
		words = util.wordsFromResponse(resp)
		v = np.zeros(self.vecDim, dtype=float)
		for word in words:
			if word in self.wordIndices:
				idx = self.wordIndices[word]
				v[idx] += 1
		return v



if __name__ == '__main__':
	ql = util.parseMohler()
	bow = BOWRegression(ql)
	print bow.run()
						
