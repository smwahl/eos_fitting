#!/Library/Frameworks/Python.framework/Versions/2.7/bin/python


from sys import *
from numpy import *
# from matplotlib import pyplot
from jlab_library import *

# Sean Wahl
# Thu Jun 20 11:02:28 PDT 2013
# Uses a fit equation of state to correct a given cell volume by a given change 
# in pressure

# Usage: polytrope_correct.py filename 'V index' 'P current' [ 'V current' 'P current'] ...

def readcols(fname,cols):
    output = []
    try:
        for line in file(fname):
            line = line.split()
            for i in range(0,len(cols)):
                output(i).append(line[cols(i)])
    except: 
        print 'Filename must be a string, column must be an integer in ramge'
                


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
#         plotx = linspace(min(x), max(x), 1000)
        if not 'Guess Failed' in fit[1]:
#            pyplot.figure()
#             pyplot.plot(plotx, [func(fit[0], j) for j in plotx], 'g-', linewidth=3)
#             pyplot.errorbar(x, y, ysigma, fmt='b.')
#            print func(fit[0],4000)
            param_value.append(fit)
        else:
            print 'Fit failed'
#             pyplot.errorbar(x, y, ysigma, fmt='b.')
#             pyplot.plot(plotx, [func(guess, k) for k in plotx], 'r-')
            param_value.append(guess) 
        param_name = fitnames[i]
        #print func(fit[0],4000)
        #print func(param_value[0],4000)
        #testf.append(lambda x: func(param_value[0],x)) 
        #print testf[i](4000)
#        params.append([param_name, param_value[i], lambda x: funcs[i](param_value[i][0],x)])
        
#    params = [ [ name value lambda x: func(value[0],x)] for name in fitnames for func in funcs for value in param_value]
#    params = [ [ fitnames[i], param_value[i], lambda x: funcs[i](param_value[i][0],x)] for i in range(0,len(funcs)]
    xlin = lambda x: lin(param_value[0][0],x)
    xpoly = lambda x: poly(param_value[1][0],x)
    params.append( [fitnames[0], param_value[0], xlin])
    params.append( [fitnames[1], param_value[1], xpoly])

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





args = argv[1:]
files = []
xs = []

files.append(str(argv[1]))
Vcol = int(argv[2])
Pcol = int(argv[3])
corrs = argv[4:]

# for arg in argv[4:]:
#     try:
#         xs.append(double(arg))
#     except:
#         print 'Problem with input', arg


lin = lambda v, x: v[0] + v[1]*x
poly  = lambda v, x: v[0] * x ** v[1]

ilin = lambda v, y: (-v[0] + y)/v[1]
ipoly = lambda v, y: ( y / v[0] ) ** (1/v[1])

functions = [ [ lin, poly ], ["linear","polytrope"] ]
ifunctions = [ [ ilin, ipoly ], ["linear","polytrope"] ]


# fignum = 0

for pvfile in files:
    data = genfromtxt(str(pvfile), unpack=True)

    p = data[Pcol]
#     psigma  = data[1]
    v = data[Vcol]


    print pvfile, ': '
    print '      V             P'
    for i in range(0, len(p)):
        print '    ',v[i], ' ', p[i]

    print ''
    ysigma = array([0.1 for item in v]) # set in case inverse fit is needed

    guess = [1.0, 0.01 ]

# fit v(p)
#    pyplot.figure()
#     pyplot.figure(fignum)
#     fignum = fignum + 1
    params = fit(p, v, ysigma, [ guess, guess],functions)

    print 'Polytrope fit Parameters : ', params[1][1][0].tolist()

    # Fit parameters for correction
    polyParam = params[1][1][0].tolist()

# fit p(v)
# When to be found in terms of the original dependent variable
#    pyplot.figure()
#     pyplot.figure(fignum)
#     fignum = fignum + 1
#     params2 = fit(v, p, ysigma,[params[0][1][0].tolist(), params[1][1][0].tolist()],ifunctions)

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

#     # Find
#     volumes = [ ]
#     cubic_as = [ ] 
#     for pt in :
#         po = p[0]
#         idx = 0
#         for i in range(1,len(p)):
#             if ( pt - p[i]  )**2 < (po - pt )**2:
#                 po =  p[i]
#                 idx = i
#                 
#         vo = v[idx]       
#         print "Closest point in fit dataset: p=", po, " v=",vo
#         for i in range( 1, len(params2)): # only the polytrope
#     #     try:
#             esto = functions[0][i](polyParam,po)
#             shift = vo - esto 
#             est = functions[0][i](polyParam,pt)
#             shift_est = est + shift
# #             error1 =  ferror(functions[0][i],pt,params2[i][1][0].tolist(), params2[i][1][1]) 
# #             error2 =  ferror_s(functions[0][i],pt,params2[i][1][0].tolist(), params2[i][1][1],po,vo) 
# #             error3 = ferror_s(functions[0][i],pt,params[i][1][0].tolist(), params2[i][1][1],po,vo)
#             
# 
# #             pyplot.figure(fignum-2)            
# #             pyplot.plot([pt,po], [shift_est,vo] , 'k--', linewidth=3)
# 
# # pyplot.show()


    volumes = [ ]
    cubic_as = [ ] 

    while len(corrs) >= 2:
        vcurr = float(corrs[0])
        pcurr = float(corrs[1])
        corrs = corrs[2:]

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
        



#     print 'Volumes: ', volumes
#     print 'Cubic a: ', cubic_as


