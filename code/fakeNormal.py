from regressionModel import MultipleRegressionJudge

import random
import scipy.stats


class FakeNormalQuestion(object):
	def __init__(self, questionID, answer=1, midpoint_rating=1200, variance=0.1):
		self.questionID = questionID
		self.answer = answer
		self.midpoint_rating = midpoint_rating
		self.variance = variance


	def probAnswerCorrect(self, competitorRating):
		return scipy.stats.norm(self.midpoint_rating, self.variance).cdf(competitorRating)


class FakeNormalSubject(object):
	def __init__(self, rating, initialRating=1200):
		self.hiddenRating = rating
		self.rating = initialRating


	def answerQuestion(self, fakeNormalQuestion):
		pAC = fakeNormalQuestion.probAnswerCorrect(self.hiddenRating)
		answerIsCorrect = random.random() <= pAC
		if answerIsCorrect:
			return fakeNormalQuestion.answer
		return int(not fakeNormalQuestion.answer)


class FakeNormalCompetitor(object):
	def __init__(self, questionBank, hiddenRating, initialRating=1200):
		self.questionBank = questionBank
		self.hiddenRating = hiddenRating
		self.rating = initialRating
		self.judge = None
		self.subject = None


	def init(self):
		self.judge = MultipleRegressionJudge(self.questionBank)
		self.subject = FakeNormalSubject(self.hiddenRating, self.rating)


	def finishCompetition(self, actualRating):
		self.judge.updatePriorModel(actualRating)