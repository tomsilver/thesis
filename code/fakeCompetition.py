from globalVals import CORRECT_SCALE, NUM_COMPETITORS, QUESTION_LIMIT, TRIALS
from utils import elo

import fakeNormal
import myplot
import random
import time


def main():
	maxQuestionAvg = 2000
	minQuestionAvg = 400
	questionInterval = (maxQuestionAvg-minQuestionAvg)/QUESTION_LIMIT
	questionBank = [fakeNormal.FakeNormalQuestion(i, midpoint_rating=r) for i,r in enumerate(range(minQuestionAvg, maxQuestionAvg, questionInterval))]
	assert len(questionBank) == QUESTION_LIMIT

	maxCompAvg = 1800
	minCompAvg = 600
	compInterval = (maxCompAvg-minCompAvg)/NUM_COMPETITORS	
	competitors = [fakeNormal.FakeNormalCompetitor(questionBank, r) for r in range(minCompAvg, maxCompAvg, compInterval)]
	assert len(competitors) == NUM_COMPETITORS

	for competitor in competitors:
		competitor.init()

	myplot.init()

	for t in range(TRIALS):
		selectedCompetitor1 = random.choice(competitors)
		selectedCompetitor2 = selectedCompetitor1
		while selectedCompetitor1 == selectedCompetitor2:
			selectedCompetitor2 = random.choice(competitors)

		actualRatingof1 = selectedCompetitor1.hiddenRating
		actualRatingof2 = selectedCompetitor2.hiddenRating
		currentRatingof1 = selectedCompetitor1.rating
		currentRatingof2 = selectedCompetitor2.rating

		print "Facing off competitor (", currentRatingof1, 
		print "/", actualRatingof1, ") vs. competitor (",
		print currentRatingof2, "/", actualRatingof2, ")"

		# 1 judges 2
		numCorrectof2 = selectedCompetitor1.judge.judgeCompetitor(selectedCompetitor2.subject)
		estRatingof2 = selectedCompetitor1.judge.guessCompetitorRating()
		
		# 2 judges 1
		numCorrectof1 = selectedCompetitor2.judge.judgeCompetitor(selectedCompetitor1.subject)
		estRatingof1 = selectedCompetitor2.judge.guessCompetitorRating()

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

			# myplot.plotCompRatings(competitors)
			# myplot.draw()
			# time.sleep(0.5)
			# myplot.close()


		selectedCompetitor1.finishCompetition(currentRatingof2)
		selectedCompetitor2.finishCompetition(currentRatingof1)

	myplot.plotCompRatings(competitors)
	myplot.show()
	

if __name__ == '__main__':
	main()

