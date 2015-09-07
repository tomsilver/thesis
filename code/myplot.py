from globalVals import TRIALS
from matplotlib.colors import ListedColormap
from matplotlib import pyplot as plt

import numpy as np

def title(titleStr):
	plt.title(titleStr)

def axlabel(xlab, ylab):
	plt.xlabel(xlab)
	plt.ylabel(ylab)

def plot(x, y):
	plt.plot(x, y)

def init():
	plt.ion()
	plt.show()

def show(block=True):
	plt.show(block)

def draw():
	plt.draw()

def close():
	plt.close()

def plotRatings(competitors):
	N = len(competitors)
	currentRatings = [c.rating for c in competitors]
	compNames = [c.id for c in competitors]

	ind = np.arange(N)  # the x locations for the groups
	width = 0.35       # the width of the bars

	fig, ax = plt.subplots()
	rects1 = ax.bar(ind, currentRatings, width, color='r')

	# add some text for labels, title and axes ticks
	ax.set_ylabel('Rating')
	ax.set_title('Current Ratings ('+str(TRIALS)+' games)')
	ax.set_xticks(ind+width)
	ax.set_xticklabels(compNames)

	def autolabel(rects):
	    # attach some text labels
	    for rect in rects:
	        height = rect.get_height()
	        ax.text(rect.get_x()+rect.get_width()/2., 1.05*height, '%d'%int(height),
	                ha='center', va='bottom')

	autolabel(rects1)

def plotCompRatings(competitors):
	N = len(competitors)
	currentRatings = [c.rating for c in competitors]
	actualRatings = [c.hiddenRating for c in competitors]

	ind = np.arange(N)  # the x locations for the groups
	width = 0.35       # the width of the bars

	fig, ax = plt.subplots()
	rects1 = ax.bar(ind, currentRatings, width, color='r')
	rects2 = ax.bar(ind+width, actualRatings, width, color='y')

	# add some text for labels, title and axes ticks
	ax.set_ylabel('Rating')
	ax.set_title('Ratings Tend Towards Actual Hidden Ratings ('+str(TRIALS)+' games)')
	ax.set_xticks(ind+width)
	ax.get_xaxis().set_visible(False)

	ax.legend( (rects1[0], rects2[0]), ('Current', 'Actual'), loc=4)

	def autolabel(rects):
	    # attach some text labels
	    for rect in rects:
	        height = rect.get_height()
	        ax.text(rect.get_x()+rect.get_width()/2., 1.05*height, '%d'%int(height),
	                ha='center', va='bottom')

	autolabel(rects1)
	autolabel(rects2)

def plotLabeledPoints((X, y)):
	cm = plt.cm.RdBu
	cm_bright = ListedColormap(['#FF0000', '#0000FF'])
	# Plot the points
	plt.scatter(X[:, 0], X[:, 1], c=y, cmap=cm_bright)
	plt.show(block=False)
