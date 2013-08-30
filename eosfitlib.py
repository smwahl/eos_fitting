#/u/smwahl/packages/anaconda/bin/python
#/Library/Frameworks/Python.framework/Versions/2.7/bin/python

from sys import *
from numpy import *
from matplotlib import pyplot
from jlab_library import *

# Sean Wahl
# Thu Jun 20 11:02:28 PDT 2013
# Functions using fitting library jlab_library to fit models to EOS data.
# For use by polytrope_fit.py, polytrope_fitV.py, polytrope_shift.py, etc.

def readcols(fname,cols):
    output = []
    try:
        for line in file(fname):
            line = line.split()
            for i in range(0,len(cols)):
                output(i).append(line[cols(i)])
    except: 
        print 'Filename must be a string, column must be an integer in ramge'
                

# function to fit P(V) or V(P) to a number of specified functional forms
# x and y contain datapoints to fit y(x), y sigma are errorbars on y (if known)
# guesses 
# functions contains names and functional forms of models
# returns set of parameters for each type of function to be fit

# current implementation doesn't handle the return of fit functions in a 
# general manner

def fit(x, y, ysigma, guesses, functions):
    funcs = functions[0]
    fitnames = functions[1]
    param_value = []
    testf = []
    params = []
    for i in range(0, len(funcs)):
        func = funcs[i]
        guess = guesses[i]
        cf = CurveFit(func, guess, (x, y, ysigma))
        fit = cf.minimize_chi_squared()
        if not 'Guess Failed' in fit[1]:
            param_value.append(fit)
        else:
            print 'Fit failed'
            param_value.append(guess) 
        param_name = fitnames[i]
        #print func(fit[0],4000)
        #print func(param_value[0],4000)
        #testf.append(lambda x: func(param_value[0],x)) 
        #print testf[i](4000)

#    xlin = lambda x: lin(param_value[0][0],x)
#    xpoly = lambda x: poly(param_value[1][0],x)
#    params.append( [fitnames[0], param_value[0], xlin])
#    params.append( [fitnames[1], param_value[1], xpoly])

    for i in range(0, len(funcs)):
        func = funcs[i]
        params.append([fitnames[i], param_value[i], lambda x: func(param_value[i][0],x)])

    return params


# same as fit() with plotting of results via matplotlib turned on
def fitandplot(x, y, ysigma, guesses, functions):
    funcs = functions[0]
    fitnames = functions[1]
    param_value = []
    testf = []
    params = []
    for i in range(0, len(funcs)):
        func = funcs[i]
        guess = guesses[i]
        cf = CurveFit(func, guess, (x, y, ysigma))
        fit = cf.minimize_chi_squared()
        plotx = linspace(min(x), max(x), 1000)
        if not 'Guess Failed' in fit[1]:
            pyplot.figure()
            pyplot.plot(plotx, [func(fit[0], j) for j in plotx], 'g-', linewidth=3)
            pyplot.errorbar(x, y, ysigma, fmt='b.')
#            print func(fit[0],4000)
            param_value.append(fit)
        else:
            print 'Fit failed'
            pyplot.errorbar(x, y, ysigma, fmt='b.')
            pyplot.plot(plotx, [func(guess, k) for k in plotx], 'r-')
            param_value.append(guess) 
        param_name = fitnames[i]
        #print func(fit[0],4000)
        #print func(param_value[0],4000)
        #testf.append(lambda x: func(param_value[0],x)) 
        #print testf[i](4000)

#    xlin = lambda x: lin(param_value[0][0],x)
#    xpoly = lambda x: poly(param_value[1][0],x)
#    params.append( [fitnames[0], param_value[0], xlin])
#    params.append( [fitnames[1], param_value[1], xpoly])

    for i in range(0, len(funcs)):
        func = funcs[i]
        params.append([fitnames[i], param_value[i], lambda x: func(param_value[i][0],x)])


    return params




# calculates the error of a function of a collection of combinations of intependent uncertainties
def ferror(func,x,var,dvar):
    yo = func(var,x)
#    print yo
#    print var
#    print dvar
    dyvar = []
    for i in range(0,len(var)):
        var2 = [v for v in var ]
#        print var[i] + dvar[i]
        var2[i] = var[i] + dvar[i]
#        print var, var2
        dyvar.append(func(var2,x) - yo)
#    print dyvar    
    dyvarsqr = [ dyv**2 for dyv in dyvar ]
    dy = sum(dyvarsqr)**(1.0/2)
#    print dyvarsqr, sum(dyvarsqr), dy
    return dy

# Takes into account shifting the fit to cross through the nearest point
def ferror_s(func,x,var,dvar,xclose,yclose):
    yo = func(var,x)
    shift = yclose - func(var,xclose)
    yoshift = yo + shift
#    print yo
#    print var
#    print dvar
#    print yo, ' ', yoshift
    dyvar = []
    for i in range(0,len(var)):
        var2 = [v for v in var ]
#        print var[i] + dvar[i]
        var2[i] = var[i] + dvar[i]
#        print var, var2
        # takes into account shifting fit to closest value
        shift2 = yclose - func(var2,xclose) 
        dyvar.append(func(var2,x) + shift2 - yoshift)
#    print dyvar    
    dyvarsqr = [ dyv**2 for dyv in dyvar ]
    dy = sum(dyvarsqr)**(1.0/2)
#    print dyvarsqr, sum(dyvarsqr), dy
    return dy



