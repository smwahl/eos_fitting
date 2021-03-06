#! /u/smwahl/packages/anaconda/bin/python
# /Library/Frameworks/Python.framework/Versions/2.7/bin/python

# Sean Wahl
# Thu Jun 20 11:02:28 PDT 2013
# Shifts a set of PV EOS points in order to pass through an additional point.
# Useful for guessing the EOS at a different temperature with only one new data
# point. For a given file then gives an estimated volume for the target pressure
# at the new 

# Note this implementation uses absolute differences in pressure to shift the
# EOS by a constant amount.

# Usage: polytrope_shift.py filename 'V index' 'P current' [ 'V current' 'P current', 'P target'] ...

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
corrs = argv[4:]

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

    # Fit parameters to use for correction
    polyParam = params[1][1][0].tolist()

    volumes = [ ]
    cubic_as = [ ] 

    # shift EOS points by amount neccessary to have curve pass through 
    # the given PV condition
    while len(corrs) >= 2:
        vcurr = float(corrs[0])
        pcurr = float(corrs[1])
        ptar = float(corrs[2])
        corrs = corrs[3:]

        print vcurr, pcurr

        vo = vcurr
        po = ifunctions[0][1](polyParam,vo)
        pshift = pcurr - po
        print str(params[1][0]), ' Vcur= ', vo, ' Pcur= ',pcurr,' Pfit= ',po,' Pshift= ', pshift

        pnew = [ i + pshift for i in p ]
        vnew = [ i for i in v ]
        print vnew
        pnew.append(pcurr)
        vnew.append(vcurr)
        
        print 'New (shifted) datapoints'
        for i in range(len(vnew)):
            print '    ',pnew[i], ' ', vnew[i]

        
        # Estimate the volume at the target pressure as:
        # V(Ptarget-Pshift) using the original fit parameters
        # This should be identical to running the algorithm used in
        # algorithm in polytrope_fit.py since the shifted equation of state
        # is not independent from the new data point.
        
        # the only difference would occur when one of the shifted data points
        # is closer to the target pressure than the one used to shift the EOS.
        # The implemented method is preferred since it uses the result
        # for the new condition as the anchor for estimating V.

        print 'Estimating volume at target pressure: ', ptar 

        vest = functions[0][1](polyParam,ptar-pshift)

        print '    Vest = ', vest

        volumes.append(vest)
        cubic_as.append(vest**(1.0/3))

        if makeplots == 1:
            pyplot.figure(2)

            x = pnew + [ po, pcurr, ptar]
            pyplot.plot()
            plotx = linspace(min(x), max(x), 1000)
            pyplot.plot(plotx,  [ functions[0][1](polyParam, j-pshift) for j in plotx], 'c-', linewidth=3)

            pyplot.plot(po,vo,'k*')
            pyplot.plot(pcurr,vcurr,'k*')
            pyplot.plot(ptar,vest,'r*')

    # Print results for all corrections using the file
    print 'Volumes: ', volumes
    print 'Cubic a: ', cubic_as

if makeplots == 1:
#    f2 = pyplot.figure(2)
#    f2.show()
    pyplot.show()

    
