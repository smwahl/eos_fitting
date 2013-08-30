import os
import matplotlib.pyplot as pyplot
from numpy import *
from scipy.optimize import leastsq, fsolve

c = 3e8 #m/s

def avgAndStd(a_list):
	std_l = []
	avg_l = []
	for i in range(0, len(a_list[0])):
		nums = []
		for j in range(0, len(a_list)):
			nums.append(a_list[j][i])
		std_l.append(std(nums))
		avg_l.append(average(nums))
	return avg_l, std_l


def setScentificNotation():
	ax = pyplot.gca()
	ax.ticklabel_format(style='sci', scilimits=(0,0), axis='y')

	
class CurveFit:
	def __init__(self, fit_function, initial_guess, args, fit_function_deriv=None, sigmaxInput = None):
		self.func = fit_function

		self.v_0 = initial_guess
		self.args = args
		if not sigmaxInput == None:	
			self.func_deriv = fit_function_deriv
			self.args = (self.args[0], self.args[1], sigmaxInput, self.args[2])
			self.chi_squared = lambda v, x, y, sigma_x, sigma_y: (y - self.func(v,x))/sqrt( sigma_y**2 + 	(self.func_deriv(v,x)*sigma_x)**2 )

			# (y - self.func(v,x))/sigma
		else: 
			self.chi_squared = lambda v, x, y, sigmay: (y - self.func(v,x))/sigmay


	def minimize_chi_squared(self):
		v = leastsq(self.chi_squared, self.v_0,  args=self.args, full_output=1)
		self.v_final = v[0]
		error = []
		#print v
		if not v[1] == None:
			for i in range(len(v[1])):
				error.append(sqrt(v[1][i][i]))


			return (self.v_final, error, self.sum_chi_squared(self.v_final, self.args))
		return (self.v_0, 'Guess Failed. Try again')

	def sum_chi_squared(self, v, args):
		x = args[0]
		y = args[1]
		sigma_x = args[2]
		if len(args) == 4:
			sigma_y = args[3]
		dof = len(x) - len(v)

		pre_sum = []
		for i in range(len(x)):
			if len(args) == 4:
			 	pre_sum.append((self.chi_squared(v,x[i],y[i],sigma_x[i],sigma_y[i]))**2)
			else:
				pre_sum.append((self.chi_squared(v,x[i],y[i],sigma_x[i]))**2)
				#print (self.chi_squared(v,x[i],y[i],sigma_x[i]))**2
	 	return array(pre_sum).sum() / dof

	def plot_fit(self):
		X = linspace(min(self.args[0]), max(self.args[0]), 50)
		pyplot.figure()
		pyplot.plot(self.args[0], self.args[1], 'ro', X, self.func(self.v_final, X))


