from globalVals import CORRECT_SCALE, QUESTION_LIMIT, TRIALS
from utils import elo

import myplot
import random

class BaseModelOfCompetitor(object):
	def __init__(self, priorModel):
		self.currentModel = priorModel
		self.history = {} # dict of questions and answers


	def update(self, question, answer):
		raise UnimplementedError


	def guessRating(self):
		raise UnimplementedError


class Judge(object):
	def __init__(self, questionBank, priorModel):
		self.questionBank = questionBank
		self.priorModel = priorModel
		self.modelOfCurrentCompetitor = None
		self.ModelOfCompetitor = BaseModelOfCompetitor


	def _chooseNextQuestion(self):
		raise UnimplementedError


	def judgeCompetitor(self, competitor):
		self.currentQuestion = 0
		self.modelOfCurrentCompetitor = self.ModelOfCompetitor(self.priorModel)
		
		competitorCorrect = 0

		for _ in range(QUESTION_LIMIT):
			question = self._chooseNextQuestion()
			competitorAnswer = competitor.answerQuestion(question)
			competitorCorrect += int(competitorAnswer == question.answer)
			self.modelOfCurrentCompetitor.update(question, competitorAnswer)

		return competitorCorrect

	def guessCompetitorRating(self):
		expectedRating = self.modelOfCurrentCompetitor.guessRating()
		return expectedRating


	def updatePriorModel(self, actualRating):
		pass



def runGame(competitors):
	myplot.init()

	for t in range(TRIALS):
		selectedCompetitor1 = random.choice(competitors)
		selectedCompetitor2 = selectedCompetitor1
		while selectedCompetitor1 == selectedCompetitor2:
			selectedCompetitor2 = random.choice(competitors)

		currentRatingof1 = selectedCompetitor1.rating
		currentRatingof2 = selectedCompetitor2.rating

		print "Facing off competitor (", currentRatingof1, 
		print "/", selectedCompetitor1.id, ") vs. competitor (",
		print currentRatingof2, "/", selectedCompetitor2.id, ")"


		# 1 judges 2
		numCorrectof2 = selectedCompetitor1.judge.judgeCompetitor(selectedCompetitor2.subject)
		estRatingof2 = selectedCompetitor1.judge.guessCompetitorRating()
		selectedCompetitor2.totalCorrectAnswers += numCorrectof2

		# 2 judges 1
		numCorrectof1 = selectedCompetitor2.judge.judgeCompetitor(selectedCompetitor1.subject)
		estRatingof1 = selectedCompetitor2.judge.guessCompetitorRating()
		selectedCompetitor1.totalCorrectAnswers += numCorrectof1

		# Cannot predict on the first time
		if estRatingof1 is not None and estRatingof2 is not None:

			score1 = CORRECT_SCALE*numCorrectof1-abs(estRatingof2-currentRatingof2)
			score2 = CORRECT_SCALE*numCorrectof2-abs(estRatingof1-currentRatingof1)

			if score1 > score2:
				print "First competitor is winner!"
				score1 = 1.0
				score2 = 0.0

			elif score2 > score1:
				print "Second competitor is winner!"
				score1 = 0.0
				score2 = 1.0

			else:
				print "Draw!"
				score1 = 0.5
				score2 = 0.5

			newRating1, newRating2 = elo(score1, score2, currentRatingof1, currentRatingof2)
			selectedCompetitor1.rating = newRating1
			selectedCompetitor2.rating = newRating2

			# myplot.plotRatings(competitors)
			# myplot.draw()
			# time.sleep(0.5)
			# myplot.close()


		selectedCompetitor1.finishCompetition(currentRatingof2)
		selectedCompetitor2.finishCompetition(currentRatingof1)

	for competitor in competitors:
		print competitor.id,
		print ":",
		print competitor.totalCorrectAnswers

	myplot.plotRatings(competitors)
	myplot.show()
