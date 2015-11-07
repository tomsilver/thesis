from questions import *

import os



def clean_str(s):
	s = s.replace("\n", "")
	s = s.replace("<br>", "")
	return s


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
				total_resp=24):

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

	for score in respondent_scores:
		respondents.append(Respondent(score))

	# add responses
	for ridx, resp in enumerate(respondents):
		for qid in questions_dict:
			question = questions_dict[qid]
			answer = all_answers_dict[qid][ridx]
			question.addResponse(Response(answer, resp))

	return ql


if __name__ == '__main__':
	ql = parseMohler()
