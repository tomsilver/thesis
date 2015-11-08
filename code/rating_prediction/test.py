from comprehensivePrediction import CBOWRegression
from questions import *
from questionBasedPrediction import SentenceSimilarityPredictor
from responseBasedPrediction import NGramRegression


def onePerfectResponse():
	"""Training is one perfect response. Test is same response."""
	trainRespondent = Respondent("train", 1.0)
	testRespondent = Respondent("test", 1.0)

	trainQuestion = Question("what?", "Hello, world")
	testQuestion = Question("what?", "Hello, world")

	trainQuestionList = QuestionList([trainQuestion])
	testQuestionList = QuestionList([testQuestion])

	trainResponse = Response("Hello, world", trainQuestion, trainRespondent)
	testResponse = Response("Hello, world", testQuestion, testRespondent)

	trainQuestion.addResponse(trainResponse)
	testQuestion.addResponse(testResponse)

	regr = NGramRegression(None, 1)
	ssl = SentenceSimilarityPredictor(None)
	cbow = CBOWRegression(None)
	regrError = regr.run(trainQuestionList, testQuestionList)
	sslError = ssl.run(trainQuestionList, testQuestionList)
	cbowError = cbow.run(trainQuestionList, testQuestionList)

	assert regrError == 0.0, regrError
	assert sslError == 0.0, sslError
	assert cbowError == 0.0, cbowError


def onePositiveOneNegative():
	"""Training is one perfect response and one wrong response. 
	Tests are same responses."""
	posTrainRespondent = Respondent("posTrain", 1.0)
	negTrainRespondent = Respondent("negTrain", 0.0)
	posTestRespondent = Respondent("posTest", 1.0)
	negTestRespondent = Respondent("negTest", 0.0)

	trainQuestion = Question("what?", "Hello, world")
	testQuestion = Question("what?", "Hello, world")

	trainQuestionList = QuestionList([trainQuestion])
	testQuestionList = QuestionList([testQuestion])

	posTrainResponse = Response("Hello, world", trainQuestion, posTrainRespondent)
	negTrainResponse = Response("Poop shoes", trainQuestion, negTrainRespondent)
	posTestResponse = Response("Hello, world", testQuestion, posTestRespondent)
	negTestResponse = Response("Poop shoes", testQuestion, negTestRespondent)

	trainQuestion.addResponse(posTrainResponse)
	trainQuestion.addResponse(negTrainResponse)
	testQuestion.addResponse(posTestResponse)
	testQuestion.addResponse(negTestResponse)

	regr = NGramRegression(None, 1)
	ssl = SentenceSimilarityPredictor(None)
	cbow = CBOWRegression(None)
	regrError = regr.run(trainQuestionList, testQuestionList)
	sslError = ssl.run(trainQuestionList, testQuestionList)
	cbowError = cbow.run(trainQuestionList, testQuestionList)

	assert regrError == 0.0, regrError
	assert sslError == 0.0, sslError
	assert cbowError == 0.0, cbowError


if __name__ == '__main__':
	onePerfectResponse()
	onePositiveOneNegative()