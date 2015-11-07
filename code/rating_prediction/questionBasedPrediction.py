from gensim import corpora, models, similarities
from predictor import Predictor

import util


class QuestionBasedPredictor(Predictor):

	def compareWithIdeal(self, response, ideal):
		raise UnimplementedError

	def predict(self, X):
		y = []

		for x in X:
			avg_correct_rate = 0.0
			num_resp = len(x)
			for response, ideal in x:
				correct_rate = self.compareWithIdeal(response, ideal)
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
				x.append((resp, ideal))

			X.append(x)
			y.append(respondent.getRating())

		return X, y


class SentenceSimilarityPredictor(QuestionBasedPredictor):

	def prepare(self, train):
		self.ideal_responses = [s.getIdealResponse() for s in train.getQuestions()]
		texts = [util.str_to_word_list(s) for s in self.ideal_responses]
		self.dictionary = corpora.Dictionary(texts)
		corpus = [self.dictionary.doc2bow(text) for text in texts]
		self.lsi = models.LsiModel(corpus, id2word=self.dictionary, num_topics=3)
		self.index = similarities.MatrixSimilarity(self.lsi[corpus])

	def compareWithIdeal(self, response, ideal):
		vec_bow = self.dictionary.doc2bow(util.str_to_word_list(response))
		vec_lsi = self.lsi[vec_bow]
		sims = self.index[vec_lsi]
		ideal_idx = self.ideal_responses.index(ideal)
		return sims[ideal_idx]


if __name__ == '__main__':
	ql = util.parseMohler()
	ssp = SentenceSimilarityPredictor(ql)
	print ssp.run()
