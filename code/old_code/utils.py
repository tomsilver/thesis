def elo(score1, score2, r1, r2, K=32):
	R1 = 10.0**(r1/400)
	R2 = 10.0**(r2/400)
	e1 = R1/(R1+R2)
	e2 = R2/(R1+R2)
	n1 = int(r1 + K*(score1-e1))
	n2 = int(r2 + K*(score2-e2))
	return n1, n2