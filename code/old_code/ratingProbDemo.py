import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm
import math

def probPlayer1Wins(inc, player1 = 1200, sharedstd = 200):

	# Player 1
	mean1 = player1

	# Player 2
	mean2 = player1 + inc

	# 1 > 2
	meandiff1 = mean1 - mean2 
	sigmadiff1 = sharedstd*math.sqrt(2)

	p = (-1*meandiff1)/sigmadiff1
	return 1.0 - norm.cdf(p)

print probPlayer1Wins(-400)

# ps = []
# ps2 = []
# ds = range(-800, 800)
# for d in ds:
# 	p = probPlayer1Wins(d)
# 	ps.append(p)
# 	ps2.append(1.0-p)


# plt.xlabel("P1 Rating - P2 Rating")
# plt.ylabel("Probability of Winning")
# plt.title("Probable Outcomes of Two Player Game (std=200)")
# diff1, = plt.plot(ds, ps)
# diff2, = plt.plot(ds, ps2)
# plt.legend([diff1, diff2], ["Player 1", "Player 2"], loc=5)
# plt.show()