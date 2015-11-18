class QuestionList(object):
	def __init__(self, questions=None):
		self.questions = questions
		self.qpr = None

	def addQuestion(self, question):
		if self.questions is None:
			self.questions = [question]
		else:
			self.questions.append(question)

	def getQuestions(self):
		return self.questions

	def getQuestionsPerRespondent(self):
		if self.qpr is not None:
			return self.qpr

		self.qpr = {}

		for q in self.getQuestions():
			for r in q.getResponses():
				try:
					self.qpr[r.respondent].append(r)
				except KeyError:
					self.qpr[r.respondent] = [r]

		return self.qpr

	def prettyPrint(self):
		qpr = self.getQuestionsPerRespondent()

		for respondent in qpr:
			print "Respondent", respondent,
			print "(rating:",
			print respondent.getRating(),
			print ")"
			for resp in qpr[respondent]:
				print "Question:",
				print resp.getQuestion()
				print "Ideal:",
				print resp.getIdeal()
				print "Response:",
				print resp
				print


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
		if hasattr(self, 'responses'):
			return self.responses
		return []



class Response(str):
	def __new__(self, value, question, respondent):
		return str.__new__(self, value)
	
	def __init__(self, value, question, respondent):
		self.question = question
		self.respondent = respondent

	def getIdeal(self):
		return self.question.getIdealResponse()

	def getQuestion(self):
		return self.question

	def getRating(self):
		return self.respondent.getRating()

	def getRespondentID(self):
		return self.respondent.getID()



class Respondent(object):
	def __init__(self, rid, rating):
		self.rid = rid
		self.rating = rating

	def setRating(self, rating):
		self.rating = rating

	def getRating(self):
		return self.rating

	def getID(self):
		return self.rid

