from gensim.models import word2vec
from predictor import ConstantBestGuessPredictor, Predictor, RandomPredictor

import util


class QuestionBasedPredictor(Predictor):

	def compareWithIdeal(self, response, ideals):
		raise UnimplementedError

	def train(self, X, y):
		self.lr = util.universalRegression()
		self.lr.fit(X, y)

	def predict(self, X):
		y = self.lr.predict(X)
		for idx in range(len(y)):
			if y[idx] > 1:
				y[idx] = 1.0
			elif y[idx] < 0:
				y[idx] = 0.0
		return y

	def parseQuestionList(self, questionList):

		qpr = questionList.getQuestionsPerRespondent()

		X = []
		y = []

		for respondent, responses in qpr.items():
			x = []
			for resp in responses:
				ideal = resp.getIdeal()
				x.append(self.compareWithIdeal(resp, ideal))

			X.append(x)
			y.append(respondent.getRating())

		return X, y


class WordEditDistancePredictor(QuestionBasedPredictor):

	def compareWithIdeal(self, response, ideals):
		maxSim = 0.0
		for ideal in ideals:
			N = 1.0*max(len(response),len(ideal))
			overlap = util.editDistance(response, ideal)
			sim = 1.0 - overlap/N
			maxSim = max(maxSim, sim)
		return maxSim



class CharEditDistancePredictor(QuestionBasedPredictor):

	def compareWithIdeal(self, response, ideals):
		maxSim = 0.0
		responseStr = ' '.join(response)
		for ideal in ideals:
			idealStr = ' '.join(ideal)
			N = 1.0*max(len(responseStr), len(idealStr))
			overlap = util.editDistance(responseStr, idealStr)
			sim = 1.0 - overlap/N
			maxSim = max(maxSim, sim)
		return maxSim



class Word2VecCosine(QuestionBasedPredictor):

	def prepare(self, train):
		idealResponses = [r for s in train.getQuestions() for r in s.getIdealResponse()]
		idealSentences = [s.encode('utf-8').split() for s in idealResponses]
		self.model = word2vec.Word2Vec(idealSentences, size=10, window=5, min_count=0, workers=4)

	def compareWithIdeal(self, response, ideals):
		responseList = util.str_to_word_list(response)
		idealSentences = [s.encode('utf-8').split() for s in ideals]
		knownWords = filter(lambda s: self.model.__contains__(s), responseList)
		if len(knownWords) == 0:
			return 0

		maxSimilarity = 0
		for ideal in idealSentences:
			sim = self.model.n_similarity(ideal, knownWords)
			maxSimilarity = max(maxSimilarity, sim)

		return maxSimilarity

class TrainedWord2VecCosine(QuestionBasedPredictor):

	def prepare(self, train):
		self.model = util.getText8Model()

	def compareWithIdeal(self, response, ideals):
		responseList = util.str_to_word_list(response)
		idealSentences = [s.encode('utf-8').split() for s in ideals]
		knownWords = filter(lambda s: self.model.__contains__(s), responseList)
		if len(knownWords) == 0:
			return 0

		maxSimilarity = 0
		for ideal in idealSentences:
			known = filter(lambda s: self.model.__contains__(s), ideal)
			if len(known) == 0:
				continue
			sim = self.model.n_similarity(known, knownWords)
			maxSimilarity = max(maxSimilarity, sim)

		return maxSimilarity


class LiSemanticNets(QuestionBasedPredictor):

	def compareWithIdeal(self, response, ideals):
		maxSimilarity = 0.0
		for ideal in ideals:
			if response == ideal:
				return 1.0
			try:
				sim = util.computeLiSimilarity(response, ideal)
			except:
				sim = 0.0
			maxSimilarity = max(sim, maxSimilarity)
		return maxSimilarity


class BinaryOverlapPredictor(QuestionBasedPredictor):

	def compareWithIdeal(self, response, ideals):
		# if one word overlap, return 1.0, otherwise 0.0
		for ideal in ideals:
			for word in response.split():
				if word in ideal:
					return 1.0
		return 0.0


class FractionOverlapPredictor(QuestionBasedPredictor):

	def compareWithIdeal(self, response, ideals):
		max_overlap = 0
		responseSet = set(util.str_to_word_list(response))
		for ideal in ideals:
			idealSet = set(util.str_to_word_list(ideal))
			N = len(idealSet | responseSet)
			if N:
				this_overlap = (1.0*len(idealSet & responseSet))/N
				max_overlap = max(max_overlap, this_overlap)

		return max_overlap


if __name__ == '__main__':
	ql = util.parsePowerGrading()
	# lsn = LiSemanticNets(ql)
	# print lsn.run()


	total_err_ran = 0.0
	total_err_cbg = 0.0
	total_err_bop = 0.0
	total_err_fop = 0.0
	total_err_wed = 0.0
	total_err_ced = 0.0
	total_err_w2v = 0.0
	total_err_twv = 0.0

	for i in range(util.TRIALS):
		print "Trial", i

		ql = util.parsePowerGrading()
		ran = RandomPredictor(ql)
		cbg = ConstantBestGuessPredictor(ql)
		bop =  BinaryOverlapPredictor(ql)
		fop = FractionOverlapPredictor(ql)
		wed = WordEditDistancePredictor(ql)
		ced = CharEditDistancePredictor(ql)
		w2v = Word2VecCosine(ql)
		twv = TrainedWord2VecCosine(ql)


		total_err_ran += ran.run()
		total_err_cbg += cbg.run()
		total_err_bop += bop.run()
		total_err_fop += fop.run()
		total_err_wed += wed.run()
		total_err_ced += ced.run()
		total_err_w2v += w2v.run()
		total_err_twv += twv.run()

	print "Average Random RMSE:",
	print total_err_ran/util.TRIALS

	print "Average CBG RMSE:",
	print total_err_cbg/util.TRIALS

	print "Average BOP RMSE:",
	print total_err_bop/util.TRIALS

	print "Average FOP RMSE:",
	print total_err_fop/util.TRIALS

	print "Average WED RMSE:",
	print total_err_wed/util.TRIALS

	print "Average CED RMSE:",
	print total_err_ced/util.TRIALS

	print "Average W2V RMSE:",
	print total_err_w2v/util.TRIALS

	print "Average TWV RMSE:",
	print total_err_twv/util.TRIALS

	

