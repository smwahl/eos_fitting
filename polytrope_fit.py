#! /u/smwahl/packages/anaconda/bin/python
# /Library/Frameworks/Python.framework/Versions/2.7/bin/python

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


# lin = lambda v, x: v[0] + v[1]*x
poly  = lambda v, x: v[0] * x ** v[1]

# ilin = lambda v, y: (-v[0] + y)/v[1]
ipoly = lambda v, y: ( y / v[0] ) ** (1/v[1])

functions = [ [  poly ], ["polytrope"] ]
ifunctions = [ [  ipoly ], ["polytrope"] ]


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
    print 'Polytrope fit Parameters : ', params[0][1][0].tolist()

# fit p(v)
# When to be found in terms of the original dependent variable
#    pyplot.figure()
#     pyplot.figure(fignum)
#     fignum = fignum + 1
    params2 = fit(v, p, ysigma,[params[i][1][0].tolist() for i in range(len(ifunctions[0]))],ifunctions)

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
    for ptar in xs: # for each given target pressure
        po = p[0]
        idx = 0
        for i in range(1,len(p)): # find the index of data point closest to the target pressure
            if ( ptar - p[i]  )**2 < (po - ptar )**2:
                po =  p[i]
                idx = i
                
        vo = v[idx] #the volume corresponding to the closest pressure 

        print "Closest point in fit dataset: p=", po, " v=",vo
        for i in range( 0, len(params)): 
    #     try:
            # use a fractional shift of volume from the closest pressure in the data
            vfitclosest = functions[0][i](params[i][1][0].tolist(),po)
            shiftclosest = vo - vfitclosest 
            fracshift = shiftclosest/vfitclosest

            vfittarget = functions[0][i](params[i][1][0].tolist(),ptar)
            shifttarget = fracshift*vfittarget
            vest = vfittarget + shifttarget
#             error1 =  ferror(functions[0][i],pt,params2[i][1][0].tolist(), params2[i][1][1]) 
#             error2 =  ferror_s(functions[0][i],pt,params2[i][1][0].tolist(), params2[i][1][1],po,vo) 
#             error3 = ferror_s(functions[0][i],pt,params[i][1][0].tolist(), params2[i][1][1],po,vo)
            
            if makeplots == 1:
                pyplot.figure(i+1)            
                x = [po,ptar]
                plotx = linspace(min(x),max(x),100)
                pyplot.plot(plotx,  [ functions[i][0](params[i][1][0].tolist(), j)*(1+fracshift) for j in plotx] , 'k--', linewidth=2)
                
                pyplot.plot(po,vo,'k*')
                pyplot.plot(po,vfitclosest,'k*')
                pyplot.plot(ptar,vfittarget,'go')
                pyplot.plot(ptar,vest,'ro')


            print str(params[i][0]), ' Vfit= ', vfittarget, ' shift= ', shifttarget,' vshifted= ',vest, ' ', ' a= ',vest**(1.0/3)
            volumes.append(vest)
            cubic_as.append(vest**(1.0/3))
            
#            print "error estimates: ", error1, ' ', error2, ' ', error3
    #     except:
    #        print "Problem findint estimate for: ",params[i][1][0]

    print 'Volumes: ', volumes
    print 'Cubic a: ', cubic_as

if makeplots == 1:
#    f2 = pyplot.figure(2)
#    f2.show()
    pyplot.show()

