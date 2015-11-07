class QuestionList(object):
	def __init__(self, questions=None):
		self.questions = questions

	def addQuestion(self, question):
		if self.questions is None:
			self.questions = [question]
		else:
			self.questions.append(question)

	def getQuestions(self):
		return self.questions

	def getQuestionsPerRespondent(self):
		qpr = {}
		for q in self.getQuestions():
			for r in q.getResponses():
				try:
					qpr[r.respondent].append(r)
				except KeyError:
					qpr[r.respondent] = [r]
		return qpr



class Question(str):
	def __new__(self, value, idealResponse):
		return str.__new__(self, value)
	
	def __init__(self, value, idealResponse):
		self.idealResponse = idealResponse

	def getIdealResponse(self):
		return self.idealResponse

	def addResponse(self, response):
		if hasattr(self, 'responses'):
			self.responses.append(response)
		else:
			self.responses = [response]

	def getResponses(self):
		return self.responses



class Response(str):
	def __new__(self, value, respondent):
		return str.__new__(self, value)
	
	def __init__(self, value, respondent):
		self.respondent = respondent

	def getRating(self):
		return self.respondent.getRating()



class Respondent(object):
	def __init__(self, rid, rating):
		self.rid = rid
		self.rating = rating

	def getRating(self):
		return self.rating


