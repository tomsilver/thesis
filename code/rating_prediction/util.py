from questions import *
from stop_words import get_stop_words

import os
import random
import re

TOTAL_RESP = 24
STOP_WORDS = get_stop_words('english')


def clean_str(s):
	s = s.replace("\n", "")
	s = s.replace("<br>", "")
	s = s.lower()
	return s

def str_to_word_list(s):
	words = re.sub("[^\w]", " ",  s).split()
	words = [w for w in words if w not in STOP_WORDS]
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
				total_resp=TOTAL_RESP):

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
	for qid, question_str in question_strs:
		ideal_response = ideal_dict[qid]
		q = Question(question_str, ideal_response)
		questions_dict[qid] = q
		ql.addQuestion(q)

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


def splitQuestionList(questionList, trainingPerc=0.6):
	# THIS NEEDS TO BE IMPROVED
	order = range(TOTAL_RESP)
	random.shuffle(order)
	pivot = int(TOTAL_RESP*trainingPerc)
	trainingIdxs = sorted(order[:pivot])

	trainQuestions = []
	testQuestions = []

	for question in questionList.getQuestions():
		question_str = str(question)
		ideal_response = question.getIdealResponse()
		
		trainQuestion = Question(question_str, ideal_response)
		testQuestion = Question(question_str, ideal_response)

		for i,r in enumerate(question.getResponses()):
			if i in trainingIdxs:
				trainQuestion.addResponse(r)
			else:
				testQuestion.addResponse(r)

		trainQuestions.append(trainQuestion)
		testQuestions.append(testQuestion)

	trainQL = QuestionList(trainQuestions)
	testQL = QuestionList(testQuestions)

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

	for ngram in range(1, ngram_cap+1):
		for question in questions:
			for response in question.getResponses():
				new_words = wordsFromResponse(response, ngram)
				words.update(new_words)
	return words



if __name__ == '__main__':
	ql = parseMohler()
