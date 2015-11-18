from predictor import ConstantBestGuessPredictor, Predictor, RandomPredictor

import numpy as np
import util


class ResponseBasedPredictor(Predictor):

	def prepare(self, train):
		all_words = list(util.wordsFromQuestionList(train))
		self.wordIndices = {}
		for idx, word in enumerate(all_words):
			self.wordIndices[word] = idx
		self.vecDim = len(all_words)

	def train(self, X, y):
		self.lr = util.universalRegression()
		self.lr.fit(X, y)

	def predict(self, X):
		return self.lr.predict(X)

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


class NGramRegression(ResponseBasedPredictor):

	def __init__(self, questionList, ngram_cap=1):
		super(NGramRegression, self).__init__(questionList)
		self.ngram_cap = ngram_cap

	def prepare(self, train):
		all_words = list(util.wordsFromQuestionList(train, self.ngram_cap))
		self.wordIndices = {}
		for idx, word in enumerate(all_words):
			self.wordIndices[word] = idx
		self.vecDim = len(all_words)

	def responseToVec(self, resp):
		words = set()
		for ngram in range(1, self.ngram_cap+1):
			words |= util.wordsFromResponse(resp, ngram)

		v = np.zeros(self.vecDim, dtype=float)
		for word in words:
			if word in self.wordIndices:
				idx = self.wordIndices[word]
				v[idx] += 1
		return v


class BigramRegression(NGramRegression):

	def __init__(self, questionList):
		super(BigramRegression, self).__init__(questionList, ngram_cap=2)


class TrigramRegression(NGramRegression):

	def __init__(self, questionList):
		super(TrigramRegression, self).__init__(questionList, ngram_cap=3)



class BagOfSynsets(NGramRegression):

	def prepare(self, train):
		all_words = list(util.wordsFromQuestionList(train, self.ngram_cap))
		self.wordIndices = {}
		for idx, word in enumerate(all_words):
			for syn in util.getSyns(word):
				self.wordIndices[syn] = idx
		self.vecDim = len(all_words)



class NearestNeighbor(Predictor):

	def similarity(self, response1, response2):
		raise UnimplementedError

	def mostSimilarResponse(self, response):
		q = response.getQuestion()
		question = self.trainQuestions[q]
		rid = response.getRespondentID()
		responses = [r for r in question.getResponses() if r.getRespondentID() != rid]
		closestResponse = None
		maxSimilarity = 0.0

		for trainResponse in responses:
			sim = self.similarity(response, trainResponse)
			if sim > maxSimilarity:
				closestResponse = trainResponse
				maxSimilarity = sim

		return closestResponse

	def prepare(self, train):
		self.trainQuestions = {}
		for q in train.getQuestions():
			self.trainQuestions[str(q)] = q

	def predict(self, X):
		y = []

		for x in X:
			y.append(sum(x)/len(x))
		return y

	def parseQuestionList(self, questionList):

		qpr = questionList.getQuestionsPerRespondent()

		X = []
		y = []

		for respondent, responses in qpr.items():
			x = []
			for resp in responses:
				match = self.mostSimilarResponse(resp)
				if match is None:
					x.append(0.0)
				else:
					x.append(match.getRating())
			X.append(x)

			y.append(respondent.getRating())

		return X, y



class NearestNeighborOverlap(NearestNeighbor):

	def similarity(self, response1, response2):
		words1 = util.wordsFromResponse(response1)
		words2 = util.wordsFromResponse(response2)
		if len(words1 | words2) == 0:
			return 0.0
		overlap = (1.0*len(words1 & words2)) / len(words1 | words2)

		return overlap



class NearestNeighborCharEditDistance(NearestNeighbor):

	def similarity(self, response1, response2):
		response1Str = ' '.join(response1)
		response2Str = ' '.join(response2)
		l = 1.0*len(response1)+len(response2)
		overlap = (l-util.editDistance(response1Str, response2Str))/l

		return max(0, overlap)


class NearestNeighborWordEditDistance(NearestNeighbor):

	def similarity(self, response1, response2):
		l = 1.0*len(response1)+len(response2)
		overlap = (l-util.editDistance(response1, response2))/l

		return max(0, overlap)


if __name__ == '__main__':
	total_err_ran = 0.0
	total_err = 0.0
	total_err1 = 0.0
	total_err2 = 0.0
	total_err_nno = 0.0
	total_err_nnced = 0.0
	total_err_nnwed = 0.0
	total_err_bos = 0.0

	for i in range(util.TRIALS):
		print "Trial", i

		ql = util.parsePowerGrading()
		ran = RandomPredictor(ql)
		bow = ConstantBestGuessPredictor(ql)
		bow1 = NGramRegression(ql, 1)
		bow2 = NGramRegression(ql, 2)
		nno = NearestNeighborOverlap(ql)
		nnced = NearestNeighborCharEditDistance(ql)
		nnwed = NearestNeighborWordEditDistance(ql)
		bos = BagOfSynsets(ql)

		total_err_ran += ran.run()
		total_err += bow.run()
		total_err1 += bow1.run()
		total_err2 += bow2.run()
		total_err_nno += nno.run()
		total_err_nnced += nnced.run()
		total_err_nnwed += nnwed.run()
		total_err_bos += bos.run()

	print "Average Random RMSE:",
	print total_err_ran/util.TRIALS

	print "Average CBG RMSE:",
	print total_err/util.TRIALS

	print "Ngram 1 Average RMSE:",
	print total_err1/util.TRIALS

	print "Ngram 2 Average RMSE:",
	print total_err2/util.TRIALS

	print "NearestNeighborOverlap Average RMSE:",
	print total_err_nno/util.TRIALS

	print "NearestNeighborCharEditDistance RMSE:",
	print total_err_nnced/util.TRIALS

	print "NearestNeighborWordEditDistance RMSE:",
	print total_err_nnwed/util.TRIALS

	print "BagOfSynsets RMSE:",
	print total_err_bos/util.TRIALS




						
