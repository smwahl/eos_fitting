#! /u/smwahl/packages/anaconda/bin/python
# /Library/Frameworks/Python.framework/Versions/2.7/bin/python

'''Sean Wahl
Fri Aug 30 16:58:46 PDT 2013
Shifts a set of PV EOS points in order to pass through an additional point.
Useful for guessing the EOS at a different temperature with only one new data
point. For a given file then gives an estimated volume for the target pressure. 

Note this implementation uses fractional differences in volume (assumes a constant
value for the volumetric coefficient of thermal expansion) when shifting the fit
curve to pass through the new volume

Usage: polytrope_shift.py filename 'V index' 'P current' 'V multiplier' 'P multiplier' [ 'V current' 'P current', 'P target'] ... '''

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

# read in parameters from commandline
files.append(str(argv[1]))
Vcol = int(argv[2])
Pcol = int(argv[3])
vmult = float(argv[4]) # multiple for shifted data
corrs = argv[5:]
#pmult = float(argv[5])
#corrs = argv[6:]

# lin = lambda v, x: v[0] + v[1]*x
poly  = lambda v, x: v[0] * x ** v[1]  # V(P)

# corrected EOS, f = ( observed dP) / (predicted dP)
poly_corr = lambda v, x, f:  v[0] * (x / f) ** v[1]

# ilin = lambda v, y: (-v[0] + y)/v[1]
ipoly = lambda v, y: ( y / v[0] ) ** (1/v[1])  # P(V)

functions = [ [  poly ], ["polytrope"] ]
ifunctions = [ [ ipoly ], ["polytrope"] ]


functions = [ [ poly ], ["polytrope"] ]
ifunctions = [ [ ipoly ], ["polytrope"] ]


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

    # Fit parameters to use for correction
    polyParam = params[0][1][0].tolist()

    volumes = [ ]
    cubic_as = [ ] 

    # shift EOS points by amount neccessary to have curve pass through 
    # the given PV condition
    while len(corrs) >= 2:
        vcurr = float(corrs[0])
        pcurr = float(corrs[1])
        ptar = float(corrs[2])
        corrs = corrs[3:]

        print 'Shifting curve to V=',vcurr,' P=', pcurr

#        vo = vmult * poly_corr(polyParam,pcurr,pmult)
        vo = functions[0][0](polyParam,pcurr) # find volume on fit curve corresponding to pcurr
        
        vo = vo*vmult # multiply if shifted runs are difference cell size
        # first shift
        po = pcurr 

        shifto = vcurr - vo # volume shift at from curve at pcurr
        fracShift = shifto / vo # fractional shift (this is the constant) applied
                                  # the function

        
        print str(params[0][0]), ' Vfit= ',po,' Vshift= ', shifto, ' frac_shift= ', fracShift

        pnew = [ i for i in p ] 
        vnew = [ i*vmult*(1+fracShift) for i in v ]
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

        vcurvetar = vmult*functions[0][0](polyParam,ptar) # fit volume at vtar
#        vcurvetar = vmult *poly_corr(polyParam,ptar,pmult)
        shift = fracShift*vcurvetar
        vest = vcurvetar + shift

        print 'Vfit=',vcurvetar,' Vshift=',shift,' Vest=', vest

        volumes.append(vest)
        cubic_as.append(vest**(1.0/3))

        if makeplots == 1:
            pyplot.figure(1)

            x = pnew + [ po, pcurr, ptar]
            pyplot.plot()
            plotx = linspace(min(x), max(x), 1000)
            pyplot.plot(plotx,  [ functions[0][0](polyParam, j)*(1+fracShift) for j in plotx] ,'k--', linewidth=2 )

            pyplot.plot(po,vo,'k*')
            pyplot.plot(pcurr,vcurr,'k*')
            pyplot.plot(ptar,vcurvetar,'go')
            pyplot.plot(ptar,vest,'ro')

    # Print results for all corrections using the file
    print 'Volumes: ', volumes
    print 'Cubic a: ', cubic_as

if makeplots == 1:
#    f2 = pyplot.figure(2)
#    f2.show()
    pyplot.show()

    
