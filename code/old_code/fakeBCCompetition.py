from globalVals import BC_DIM, QUESTION_LIMIT, TRIALS
from sklearn.datasets import make_moons
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from utils import elo

import fakeBinaryClassification as fBC
import model
import myplot
import random
import time


# FOR NOW WE CAN ONLY DO 2 DIMENSIONS
TRAINING_SET = make_moons(n_samples=100, noise=0.3)

myplot.plotLabeledPoints(TRAINING_SET)


def trainSubject(subject, training_set=TRAINING_SET):
	X, y = training_set
	subject.classifier.fit(X, y)


def createBCCompetitor(compid, classifier):
	competitor = fBC.FakeBCCompetitor(compid, None, classifier)
	competitor.initSubject()
	trainSubject(competitor.subject)
	competitor.createQuestionBank(limit=QUESTION_LIMIT)
	competitor.initJudge()
	return competitor


def main():
	
	nb = createBCCompetitor("Naive Bayes", GaussianNB())
	nn = createBCCompetitor("Nearest Neighbors", KNeighborsClassifier(3))
	lsvm = createBCCompetitor("Linear SVM", SVC(kernel="linear", C=0.025))
	rbfsvm = createBCCompetitor("RBF SVM", SVC(gamma=2, C=1))
	dt = createBCCompetitor("Decision Tree", DecisionTreeClassifier(max_depth=5))

	competitors = [nb, nn, lsvm, rbfsvm, dt]

	model.runGame(competitors)
	

if __name__ == '__main__':
	main()

