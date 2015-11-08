from questions import QuestionList

import numpy as np
import util


class Predictor(object):

	def __init__(self, questionList):
		self.questionList = questionList

	def run(self, train=None, test=None):
		if train is None:
			train, test = util.splitQuestionList(self.questionList)
		
		self.prepare(train)

		trainX, trainy = self.parseQuestionList(train)
		testX, testy = self.parseQuestionList(test)
		self.train(trainX, trainy)
		preds = self.predict(testX)
		return self.evaluate(preds, np.array(testy))

	def prepare(self, train):
		pass

	def train(self, X, y):
		pass

	def predict(self, X):
		raise UnimplementedError

	def evaluate(self, preds, testy):
		rmse = np.sqrt(np.mean(np.square(preds-testy)))
		return rmse

	def parseQuestionList(self, questionList):
		raise UnimplementedError