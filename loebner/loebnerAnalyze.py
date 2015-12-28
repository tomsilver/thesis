from collections import defaultdict
from loebnerParse import getFilesAndSpeakerMaps, parseTestFromTranscriptFile
from random import shuffle
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier


def prepareLoebners(speakerFileName='speakers.txt', training_perc=0.8):

	loebners = []

	for (transcript, speakerMap) in getFilesAndSpeakerMaps(speakerFileName):
		loebner = parseTestFromTranscriptFile(transcript, speakerMap)
		loebners.append(loebner)

	shuffle(loebners)
	midIdx = int(len(loebners)*training_perc)
	trainingLoebners = loebners[:midIdx]
	testLoebners = loebners[midIdx:]

	return trainingLoebners, testLoebners


def loebnersToCharFeatures(loebners, trainingCharOrder=None):

	humanCharCounts = []
	machineCharCounts = []

	Xdata = []
	ydata = []

	allTrainingChars = set()

	for loebner in loebners:
		humanCharCount = defaultdict(int)
		machineCharCount = defaultdict(int)

		for phrase in loebner.humanConv.phraseList:
			if phrase.speaker == 'human':
				for char in phrase.phrase:
					humanCharCount[char] += 1

		for phrase in loebner.machineConv.phraseList:
			if phrase.speaker == 'machine':
				for char in phrase.phrase:
					machineCharCount[char] += 1

		humanCharCounts.append(humanCharCount)
		machineCharCounts.append(machineCharCount)

		allTrainingChars |= set(humanCharCount.keys())
		allTrainingChars |= set(machineCharCount.keys())

	if trainingCharOrder is None:
		trainingCharOrder = {}
		for i,c in enumerate(allTrainingChars):
			trainingCharOrder[c] = i

	numChars = len(trainingCharOrder)

	for humanCharCount in humanCharCounts:
		X = [0 for _ in range(numChars)]

		for c in humanCharCount:
			if c in trainingCharOrder:
				charIdx = trainingCharOrder[c]
				X[charIdx] = humanCharCount[c]

		Xdata.append(X)
		ydata.append(1)

	for machineCharCount in machineCharCounts:
		X = [0 for _ in range(numChars)]

		for c in machineCharCount:
			if c in trainingCharOrder:
				charIdx = trainingCharOrder[c]
				X[charIdx] = machineCharCount[c]

		Xdata.append(X)
		ydata.append(0)

	return Xdata, ydata, trainingCharOrder

def loebnersToDoubleCharFeatures(loebners, trainingCharOrder=None):

	humanCharCounts = []
	machineCharCounts = []

	Xdata = []
	ydata = []

	allTrainingChars = set()

	for loebner in loebners:
		humanCharCount = defaultdict(int)
		machineCharCount = defaultdict(int)

		for phrase in loebner.humanConv.phraseList:
			if phrase.speaker == 'human':
				for i in range(len(phrase.phrase)-1):
					double = phrase.phrase[i]+phrase.phrase[i+1]
					humanCharCount[double] += 1

		for phrase in loebner.machineConv.phraseList:
			if phrase.speaker == 'machine':
				for i in range(len(phrase.phrase)-1):
					double = phrase.phrase[i]+phrase.phrase[i+1]
					machineCharCount[double] += 1

		humanCharCounts.append(humanCharCount)
		machineCharCounts.append(machineCharCount)

		allTrainingChars |= set(humanCharCount.keys())
		allTrainingChars |= set(machineCharCount.keys())

	if trainingCharOrder is None:
		trainingCharOrder = {}
		for i,c in enumerate(allTrainingChars):
			trainingCharOrder[c] = i

	numChars = len(trainingCharOrder)

	for humanCharCount in humanCharCounts:
		X = [0 for _ in range(numChars)]

		for c in humanCharCount:
			if c in trainingCharOrder:
				charIdx = trainingCharOrder[c]
				X[charIdx] = humanCharCount[c]

		Xdata.append(X)
		ydata.append(1)

	for machineCharCount in machineCharCounts:
		X = [0 for _ in range(numChars)]

		for c in machineCharCount:
			if c in trainingCharOrder:
				charIdx = trainingCharOrder[c]
				X[charIdx] = machineCharCount[c]

		Xdata.append(X)
		ydata.append(0)

	return Xdata, ydata, trainingCharOrder

def runExperiment1(verbosity=0):
	trainingLoebners, testLoebners = prepareLoebners()

	trainingX, trainingY, trainingCharOrder = loebnersToCharFeatures(trainingLoebners)
	testX, testY, _ = loebnersToCharFeatures(testLoebners, trainingCharOrder)

	classifiers = [("Naive Bayes", GaussianNB()), 
				   ("Nearest Neighbors", KNeighborsClassifier(3)), 
				   ("Linear SVM", SVC(kernel="linear", C=0.025)),
				   ("RBF SVM", SVC(gamma=2, C=1)),
				   ("Decision Tree", DecisionTreeClassifier(max_depth=5))]

	scores = []

	for idc, classifier in classifiers:
		classifier.fit(trainingX, trainingY)
		score = classifier.score(testX, testY)
		scores.append(score)

		if verbosity > 0:
			print idc,
			print ":",
			print score

	return scores

def runExperiment2(verbosity=0):
	trainingLoebners, testLoebners = prepareLoebners()

	trainingX, trainingY, trainingCharOrder = loebnersToDoubleCharFeatures(trainingLoebners)
	testX, testY, _ = loebnersToCharFeatures(testLoebners, trainingCharOrder)

	classifiers = [("Naive Bayes", GaussianNB()), 
				   ("Nearest Neighbors", KNeighborsClassifier(3)), 
				   ("Linear SVM", SVC(kernel="linear", C=0.025)),
				   ("RBF SVM", SVC(gamma=2, C=1)),
				   ("Decision Tree", DecisionTreeClassifier(max_depth=5))]

	scores = []

	for idc, classifier in classifiers:
		classifier.fit(trainingX, trainingY)
		score = classifier.score(testX, testY)
		scores.append(score)

		if verbosity > 0:
			print idc,
			print ":",
			print score

	return scores

totalscores = [0.0 for _ in range(5)]
finalscores = []
trialCount = 50

for _ in range(trialCount):
	scores = runExperiment1()
	for i, s in enumerate(scores):
		totalscores[i] += s

for s in totalscores:
	finalscores.append(s/trialCount)

print finalscores



