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
	def __init__(self, rating):
		self.rating = rating

	def getRating(self):
		return self.rating


