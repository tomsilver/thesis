from matplotlib import pyplot as plt
from nltk.corpus import wordnet as wn
from questions import *
from sklearn import linear_model
from stop_words import get_stop_words

import editdistance
import notMyCode
import os
import random
import re
import xml.etree.ElementTree as ET

STOP_WORDS = get_stop_words('english')
TOTAL_RESP = 24
TRIALS = 100

universalRegression = linear_model.LinearRegression


def clean_str(s):
	s = s.replace("<br>", "")
	s = s.lower()
	s = s.rstrip()
	return s

def str_to_word_list(s):
	words = re.sub("[^\w]", " ",  s).split()
	words = [clean_str(w) for w in words if w not in STOP_WORDS]
	return words


def parseSingleMohlerFile(file_path):
	parsed = []
	with open(file_path) as f:
		for l in f.readlines():
			question_id, s = l.split(' ', 1)
			cleaned = clean_str(s)
			parsed.append((question_id, cleaned))
	return parsed


def parseMohler(base_data_dir="../../datasets/ShortAnswerGrading_v2.0/data", 
				questions_file="raw/questions",
				ideal_file="raw/answers",
				answers_file="raw/all", 
				scores_dir="scores",
				total_resp=TOTAL_RESP,
				total_questions=-1):

	# get questions
	questions_abs_file = os.path.join(base_data_dir, questions_file)
	question_strs = parseSingleMohlerFile(questions_abs_file)

	# get ideal answers
	ideal_abs_file = os.path.join(base_data_dir, ideal_file)
	ideal_dict = dict(parseSingleMohlerFile(ideal_abs_file))

	# initialize question list
	ql = QuestionList()

	# initialize questions
	questions_dict = {}
	question_count = 0
	for qid, question_str in question_strs:
		if total_questions >= 0 and question_count > total_questions:
			break

		ideal_response = ideal_dict[qid]
		q = Question(question_str, [ideal_response])
		questions_dict[qid] = q
		ql.addQuestion(q)
		question_count += 1

	# store all answers
	answer_abs_file = os.path.join(base_data_dir, answers_file)

	all_answers = parseSingleMohlerFile(answer_abs_file)
	all_answers_dict = {}
	for qid, answer in all_answers:
		if qid not in all_answers_dict:
			all_answers_dict[qid] = [answer]
		else:
			all_answers_dict[qid].append(answer)

	# create respondents list
	scores_abs_dir = os.path.join(base_data_dir, scores_dir)
	respondents = []
	respondent_scores = []

	for qid in questions_dict:

		# get scores
		score_file = os.path.join(scores_abs_dir, qid, "ave")
		with open(score_file) as f:
			scores = f.readlines()[:total_resp]

		for i, score in enumerate(scores):
			try:
				respondent_scores[i] += float(score)
			except IndexError:
				respondent_scores.append(float(score))

		# scale
		max_score = max(respondent_scores)
		min_score = min(respondent_scores)
		for i, score in enumerate(respondent_scores):
			respondent_scores[i] = (score-min_score)/(max_score-min_score)

	for idx, score in enumerate(respondent_scores):
		respondents.append(Respondent(idx, score))

	# add responses
	for ridx, resp in enumerate(respondents):
		for qid in questions_dict:
			question = questions_dict[qid]
			answer = all_answers_dict[qid][ridx]
			question.addResponse(Response(answer, question, resp))

	return ql


def parsePowerGrading(base_data_dir="../../datasets/Powergrading-1.0-Corpus", 
					  answer_key_file="questions_answer_key.tsv", 
					  responses_file="studentanswers_grades_698.tsv",
					  total_questions=-1):	

	# only certain questions are graded
	gradedQuestionIds = [1, 2, 3, 4, 5, 6, 7, 8, 13, 20]

	# initialize question list
	ql = QuestionList()

	# initialize questions
	answer_abs_file = os.path.join(base_data_dir, answer_key_file)
	questions_dict = {}
	question_count = 0
	
	with open(answer_abs_file) as f:
		for i, qline in enumerate(f.readlines()):
			if i == 0:
				continue
			qlinesplit = qline.split('\t')
			qid = qlinesplit[0]

			if int(qid) in gradedQuestionIds:
				question_str = clean_str(qlinesplit[1])
				ideal_responses = [clean_str(s) for s in qlinesplit[2:]]

				if total_questions >= 0 and question_count > total_questions:
					break

				q = Question(question_str, ideal_responses)
				questions_dict[qid] = q
				ql.addQuestion(q)
				question_count += 1

	# create responses and respondents
	responses_abs_file = os.path.join(base_data_dir, responses_file)
	respondents = []

	current_respondent = None
	current_respondent_id = None
	current_respondent_rating = 0

	with open(responses_abs_file) as f:
		for i, rline in enumerate(f.readlines()):
			if i == 0:
				continue
			rid, qid, response_str, g1, g2, g3 = rline.split('\t')

			if int(qid) in gradedQuestionIds:

				if rid != current_respondent_id:
					# we already finished previous respondent
					if current_respondent is not None:
						current_respondent.setRating(current_respondent_rating)

					# initialize next respondent
					current_respondent = Respondent(rid, 0)
					respondents.append(current_respondent)
					current_respondent_id = rid
					current_respondent_rating = 0

				current_respondent_rating += float(g1) + float(g2) + float(g3)
				question = questions_dict[qid]
				response = Response(clean_str(response_str), question, current_respondent)
				question.addResponse(response)

	# scale scores
	respondent_scores = [r.getRating() for r in respondents]

	# scale
	max_score = max(respondent_scores)
	min_score = min(respondent_scores)
	for respondent in respondents:
		scaled_score = (respondent.getRating()-min_score)/(max_score-min_score)
		respondent.setRating(scaled_score)

	return ql



def qprToQuestionList(qpr):
	"""qpr is a dictionary of respondents to responses"""
	questions = {}

	firstResponses = qpr.values()[0]

	for resp in firstResponses:
		question = resp.getQuestion()
		questionStr = str(question)
		idealResp = question.getIdealResponse()
		questionCopy = Question(questionStr, idealResp)
		questions[questionStr] = questionCopy

	for r, resps in qpr.items():
		for resp in resps:
			questionStr = str(resp.getQuestion())
			respStr = str(resp)
			question = questions[questionStr]
			response = Response(respStr, question, r)
			question.addResponse(response)

	questionList = QuestionList(questions.values())
	return questionList


def splitQuestionList(questionList, trainingPerc=0.8):
	order = range(TOTAL_RESP)
	random.shuffle(order)
	pivot = int(TOTAL_RESP*trainingPerc)
	trainingIdxs = sorted(order[:pivot])
	testingIdxs = sorted(order[pivot:])

	qpr = questionList.getQuestionsPerRespondent()
	qprItems = qpr.items()

	trainqpr = {}
	testqpr = {}

	for idx in trainingIdxs:
		k,v = qprItems[idx]
		trainqpr[k] = v

	for idx in testingIdxs:
		k,v = qprItems[idx]
		testqpr[k] = v

	trainQL = qprToQuestionList(trainqpr)
	testQL = qprToQuestionList(testqpr)

	return trainQL, testQL


def wordsFromResponse(response, ngram=1):
	words = set()
	candidates = str_to_word_list(response)
	for i in range(0, len(candidates)+1-ngram):
		candidate = ' '.join(candidates[i:i+ngram])
		words.add(candidate)
	return words


def wordsFromQuestionList(questionList, ngram_cap=1):
	words = set()

	try:
		questions = questionList.getQuestions()
	except AttributeError:
		questions = questionList

	for question in questions:
		for response in question.getResponses():
			new_words = wordsFromResponse(response, ngram_cap)
			words.update(new_words)
	return words


def plotRatingsFromQuestionList(questionList, plotTitle):
	qpr = questionList.getQuestionsPerRespondent()

	ratings = []

	for respondent in qpr.keys():
		ratings.append(respondent.getRating())

	plt.hist(ratings, 10, histtype='bar', rwidth=0.8)
	plt.title(plotTitle)
	plt.xlabel('Normalized Ratings')
	plt.ylabel('Count')
	plt.show()


def editDistance(str1, str2):
	return int(editdistance.eval(str1, str2))

def getSyns(word):
	syns = []
	for synset in wn.synsets(word):
		for lemma in synset.lemmas():
			cleanedSyn = clean_str(lemma.name())
			syns.append(cleanedSyn)
	return syns

def computeLiSimilarity(sentence1, sentence2, normalizeInfoContent=True):
	return notMyCode.similarity(sentence1, sentence2, normalizeInfoContent)

if __name__ == '__main__':
	ql = parseMohler()
	plotRatingsFromQuestionList(ql, 'Mohler Rating Distribution')
