import os

class Phrase(object):
	def __init__(self, speaker, phrase=''):
		self.speaker = speaker
		self.phrase = phrase


class Conversation(object):
	def __init__(self, subject):
		self.subject = subject
		self.phraseList = []


class LoebnerTest(object):
	def __init__(self, machineConv, humanConv):
		self.machineConv = machineConv
		self.humanConv = humanConv


def lineIsValid(line):
	return (' local ') in line or (' remote ') in line

def speakerFromLine(line, speakerMap):
	if 'remote' in line:
		if 'left' in line:
			return speakerMap['left']
		return speakerMap['right']
	if 'left' in line:
		return 'leftJudge'
	return 'rightJudge'

def charFromLine(line):
	words = line.split()
	char = words[-1]
	if char == 'space':
		return ' '
	if char == 'BackSpace':
		return 'BS'
	if char == 'CR':
		return 'EOP'
	return char

def addCharToPhrase(char, phrase):
	phrase.phrase += char

def backSpacePhrase(phrase):
	if len(phrase.phrase) > 0:
		phrase.phrase = phrase.phrase[:-2]

def addPhraseToConversation(phrase, conversation):
	conversation.phraseList.append(phrase)

def getFilesAndSpeakerMaps(speakerFileName, parentDir='transcripts'):
	speakerFile = os.path.join(parentDir, speakerFileName)
	filesAndSpeakerMaps = []
	for line in open(speakerFile):
		transcript,left,right = line.split(',')
		speakerMap = {'left': left, 'right': right.strip(' \t\n\r')}
		filesAndSpeakerMaps.append((transcript,speakerMap))
	return filesAndSpeakerMaps

def parseTestFromTranscriptFile(transcriptFileName, speakerMap, parentDir='transcripts'):

	transcriptFile = os.path.join(parentDir, transcriptFileName)

	conversations = {'machine': Conversation('machine'), 'human': Conversation('human')}
	conversations['leftJudge'] = conversations[speakerMap['left']]
	conversations['rightJudge'] = conversations[speakerMap['right']]
	
	currentPhrases = {}
	for speaker in conversations:
		currentPhrases[speaker] = Phrase(speaker)

	thisTest = LoebnerTest(conversations['machine'], conversations['human'])

	for line in open(transcriptFile):
		if lineIsValid(line):
			speaker = speakerFromLine(line, speakerMap)
			thisChar = charFromLine(line)
			thisPhrase = currentPhrases[speaker]

			# Beginning of new phrase
			if thisChar == 'EOP':
				thisConversation = conversations[speaker]
				addPhraseToConversation(thisPhrase, thisConversation)

				thisPhrase = Phrase(speaker)
				currentPhrases[speaker] = thisPhrase

			# Backspace
			elif thisChar == 'BS':
				backSpacePhrase(thisPhrase)
			
			else:
				addCharToPhrase(thisChar, thisPhrase)

	return thisTest


if __name__ == '__main__':
	for (transcript, speakerMap) in getFilesAndSpeakerMaps('speakers.txt'):
		loebner = parseTestFromTranscriptFile(transcript, speakerMap)

		print "Machine conversation"
		for phrase in loebner.machineConv.phraseList:
			print phrase.speaker,
			print ":",
			print phrase.phrase
		print

		print "Human conversation"
		for phrase in loebner.humanConv.phraseList:
			print phrase.speaker,
			print ":",
			print phrase.phrase
		print

