from globalVals import BC_DIM, QUESTION_LIMIT, TRIALS
from regressionModel import MultipleRegressionJudge

import random


class FakeBCQuestion(object):
	def __init__(self, point, pointClass):
		self.point = point
		self.answer = pointClass


class FakeBCSubject(object):
	def __init__(self, classifier, initialRating=1200):
		self.classifier = classifier
		self.rating = initialRating


	def answerQuestion(self, fakeBCQuestion):
		return self.classifier.predict(fakeBCQuestion.point)[0]
		

class FakeBCCompetitor(object):
	def __init__(self, compid, questionBank, classifier, initialRating=1200):
		self.id = compid
		self.questionBank = questionBank
		self.classifier = classifier
		self.rating = initialRating
		self.judge = None
		self.subject = None
		self.totalCorrectAnswers = 0


	def initSubject(self):
		self.subject = FakeBCSubject(self.classifier, self.rating)


	def initJudge(self):
		self.judge = MultipleRegressionJudge(self.questionBank)


	def init(self):
		self.initSubject()
		self.initJudge()


	def createQuestionBank(self, limit=QUESTION_LIMIT):
		questionBank = []
		for _ in range(limit):
			questionPoint = tuple([random.random() for _ in range(BC_DIM)])
			questionClass = self.classifier.predict(questionPoint)[0]
			question = FakeBCQuestion(questionPoint, questionClass)
			questionBank.append(question)
		self.questionBank = questionBank
		return questionBank


	def finishCompetition(self, actualRating):
		self.judge.updatePriorModel(actualRating)