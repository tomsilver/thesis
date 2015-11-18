from gensim.models import word2vec
from predictor import ConstantBestGuessPredictor, Predictor, RandomPredictor

import util


class QuestionBasedPredictor(Predictor):

	def compareWithIdeal(self, response, ideals):
		raise UnimplementedError

	def predict(self, X):
		y = []

		for x in X:
			avg_correct_rate = 0.0
			num_resp = len(x)
			for correct_rate in x:
				avg_correct_rate += correct_rate

			y.append(avg_correct_rate/num_resp)

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



# class GensimSSP(QuestionBasedPredictor):

# 	def prepare(self, train):
# 		self.ideal_responses = [r for s in train.getQuestions() for r in s.getIdealResponse()]
# 		print self.ideal_responses
# 		texts = [util.str_to_word_list(s) for s in self.ideal_responses]
# 		self.dictionary = corpora.Dictionary(texts)
# 		corpus = [self.dictionary.doc2bow(text) for text in texts]
# 		self.lsi = models.LsiModel(corpus, id2word=self.dictionary, num_topics=3)
# 		self.index = similarities.MatrixSimilarity(self.lsi[corpus])

# 	def compareWithIdeal(self, response, ideals):
# 		vec_bow = self.dictionary.doc2bow(util.str_to_word_list(response))
# 		vec_lsi = self.lsi[vec_bow]
# 		sims = self.index[vec_lsi]

# 		max_ideal = 0
# 		best_ideal = None

# 		for ideal in ideals:
# 			ideal_idx = self.ideal_responses.index(ideal)
# 			ideal_match = sims[ideal_idx]
# 			if ideal_match > max_ideal:
# 				max_ideal = ideal_match
# 				best_ideal = ideal

# 		print util.str_to_word_list(response), best_ideal, max_ideal

# 		return max_ideal


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


class LiSemanticNets(QuestionBasedPredictor):

	def compareWithIdeal(self, response, ideals):
		maxSimilarity = 0.0
		for ideal in ideals:
			if response == ideal:
				return 1.0
			sim = util.computeLiSimilarity(response, ideal)
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
	lsn = LiSemanticNets(ql)
	print lsn.run()


	# total_err_ran = 0.0
	# total_err_cbg = 0.0
	# total_err_bop = 0.0
	# total_err_fop = 0.0

	# for i in range(util.TRIALS):
	# 	print "Trial", i

	# 	ql = util.parsePowerGrading()
	# 	ran = RandomPredictor(ql)
	# 	cbg = ConstantBestGuessPredictor(ql)
	# 	bop =  BinaryOverlapPredictor(ql)
	# 	fop = FractionOverlapPredictor(ql)

	# 	total_err_ran += ran.run()
	# 	total_err_cbg += cbg.run()
	# 	total_err_bop += bop.run()
	# 	total_err_fop += fop.run()

	# print "Average Random RMSE:",
	# print total_err_ran/util.TRIALS

	# print "Average CBG RMSE:",
	# print total_err_cbg/util.TRIALS

	# print "Average BOP RMSE:",
	# print total_err_bop/util.TRIALS

	# print "Average FOP RMSE:",
	# print total_err_fop/util.TRIALS

