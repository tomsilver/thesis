from globalVals import QUESTION_LIMIT
from sklearn import linear_model

import model

class RegrModelOfCompetitor(model.BaseModelOfCompetitor):
	def __init__(self, priorModel):
		super(RegrModelOfCompetitor, self).__init__(priorModel)
		self.questionCount = 0
		self.expectedRating = None


	def batchUpdate(self):
		lastBools = sorted(self.history.values(), key=self.history.get)
		X = []
		for lastBool in lastBools:
			if lastBool:
				X.extend([1, 0])
			else:
				X.extend([0, 1])

		try:
			self.expectedRating = self.currentModel.predict(X)
		except AttributeError:
			print "Warning: no prediction made."


	def update(self, question, answer):
		self.history[question] = answer
		self.questionCount += 1
		if self.questionCount == QUESTION_LIMIT:
			self.batchUpdate()


class MultipleRegressionJudge(model.Judge):
	def __init__(self, questionBank):
		firstPrior = linear_model.Ridge(alpha=.5)

		super(MultipleRegressionJudge, self).__init__(questionBank, firstPrior)
		
		self.X = []
		self.y = []
		self.currentQuestion = 0
		self.ModelOfCompetitor = RegrModelOfCompetitor


	def guessCompetitorRating(self):
		if self.currentQuestion != QUESTION_LIMIT:
			raise("Not finished questioning, cannot predict rating yet.")

		return self.modelOfCurrentCompetitor.expectedRating


	def _chooseNextQuestion(self):
		nextQuestion = self.questionBank[self.currentQuestion]
		self.currentQuestion += 1
		return nextQuestion


	def updatePriorModel(self, actualRating):
		history = self.modelOfCurrentCompetitor.history
		lastBools = sorted(history.values(), key=history.get)
		lastX = []
		for lastBool in lastBools:
			if lastBool:
				lastX.extend([1, 0])
			else:
				lastX.extend([0, 1])

		self.X.append(lastX)
		self.y.append(actualRating)

		self.priorModel.fit(self.X, self.y)

