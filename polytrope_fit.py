#! /Library/Frameworks/Python.framework/Versions/2.7/bin/python

# Sean Wahl
# Fri Nov 30 16:01:13 PST 2012
# Changing so that equation of state is shifted to pass through closest point on the fit data


# Usage: polytrope_fit.py filename 'V index' 'P current' [ 'P target'] ...

from sys import *
from numpy import *
from matplotlib import pyplot
from jlab_library import *
from eosfitlib import *

# Options: (0 = false, 1 = true)
makeplots = 1

# start of main script
args = argv[1:]
files = []
xs = []

files.append(str(argv[1]))
Vcol = int(argv[2])
Pcol = int(argv[3])

for arg in argv[4:]:
    try:
        xs.append(double(arg))
    except:
        print 'Problem with input', arg


lin = lambda v, x: v[0] + v[1]*x
poly  = lambda v, x: v[0] * x ** v[1]

ilin = lambda v, y: (-v[0] + y)/v[1]
ipoly = lambda v, y: ( y / v[0] ) ** (1/v[1])

functions = [ [ lin, poly ], ["linear","polytrope"] ]
ifunctions = [ [ ilin, ipoly ], ["linear","polytrope"] ]


# Loop through files (in current implementation only one file allowed)
for pvfile in files:
    data = genfromtxt(str(pvfile), unpack=True)

    p = data[Pcol]
#     psigma  = data[1]
    v = data[Vcol]

    # print input data 
    print pvfile, ': '
    print '      V             P'
    for i in range(0, len(p)):
        print '    ',v[i], ' ', p[i]

    print ''
    ysigma = array([0.1 for item in v]) # set in case inverse fit is needed

    guess = [1.0, 0.01 ]

    # Fit data to models
    if makeplots == 0:
        params = fit(p, v, ysigma, [ guess, guess],functions)
    else:
        params = fitandplot(p, v, ysigma, [ guess, guess],functions)

    # Print fit parameters
    print 'Polytrope fit Parameters : ', params[1][1][0].tolist()

# fit p(v)
# When to be found in terms of the original dependent variable
#    pyplot.figure()
#     pyplot.figure(fignum)
#     fignum = fignum + 1
    params2 = fit(v, p, ysigma,[params[0][1][0].tolist(), params[1][1][0].tolist()],ifunctions)

#    params2 = params # When to be found in terms of the original independent variable
    
#    # for getting v(p) use functions, u(v) use ifunctions
#    for pt in xs:
#        print  str(pt), ':'
##        try:
#        for i in range( 0, len(params2)):
#            
#            param = params2[i]
#            estimate = functions[0][i](params[i][1][0].tolist(),pt)
#            error = ferror(functions[0][i],pt,param[1][0].tolist(), param[1][1]) 
#            print  str(param[0]), ' v= ', estimate, ' ', error,' a= ', estimate**(1.0/3.0)
##        except:
##            print  'Problem estimating value'
#
##    pyplot.draw()

    # Esto,ate vp;i,e at target pressure
    volumes = [ ]
    cubic_as = [ ] 
    for pt in xs:
        po = p[0]
        idx = 0
        for i in range(1,len(p)):
            if ( pt - p[i]  )**2 < (po - pt )**2:
                po =  p[i]
                idx = i
                
        vo = v[idx]       
        print "Closest point in fit dataset: p=", po, " v=",vo
        for i in range( 1, len(params2)): # only the polytrope
    #     try:
            esto = functions[0][i](params[i][1][0].tolist(),po)
            shift = vo - esto 
            est = functions[0][i](params[i][1][0].tolist(),pt)
            shift_est = est + shift
#             error1 =  ferror(functions[0][i],pt,params2[i][1][0].tolist(), params2[i][1][1]) 
#             error2 =  ferror_s(functions[0][i],pt,params2[i][1][0].tolist(), params2[i][1][1],po,vo) 
#             error3 = ferror_s(functions[0][i],pt,params[i][1][0].tolist(), params2[i][1][1],po,vo)
            

#             pyplot.figure(fignum-2)            
#             pyplot.plot([pt,po], [shift_est,vo] , 'k--', linewidth=3)

            print str(params[i][0]), ' estimate= ', est, ' shift= ', shift,' v= ',shift_est, ' ', ' a= ',shift_est**(1.0/3)
            volumes.append(shift_est)
            cubic_as.append(shift_est**(1.0/3))
            
#            print "error estimates: ", error1, ' ', error2, ' ', error3
    #     except:
    #        print "Problem findint estimate for: ",params[i][1][0]

    print 'Volumes: ', volumes
    print 'Cubic a: ', cubic_as

if makeplots == 1:
#    f2 = pyplot.figure(2)
#    f2.show()
    pyplot.show()

