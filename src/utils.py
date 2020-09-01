# import numpy as np
# from sklearn.gaussian_process import GaussianProcessRegressor
# from sklearn.gaussian_process.kernels import RBF, WhiteKernel
# from scipy.optimize import curve_fit


# def getCurveFit(x, y, fitDomainMin=None, fitDomainMax=None):
#     x = np.array(x)
#     y = np.array(y)

#     kernel = WhiteKernel(0.001) + RBF(1)
#     gp = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=5)
#     gp.fit(x[:, np.newaxis], y)

#     if fitDomainMin == None:
#         fitDomainMin = min(x)
#     if fitDomainMax == None:
#         fitDomainMax = max(x)

#     xFit = np.linspace(float(fitDomainMin), float(fitDomainMax), 100)

#     yFit, yStd = gp.predict(xFit[:, np.newaxis], return_std=True)
#     dyFit = 1.96 * yStd

#     return {'xFit': list(xFit), 'yFit': list(yFit), 'dyFit': list(dyFit)}


from kapteyn import kmpfit
import numpy as np


def getCurveFit(x, y, fitDomainMin=None, fitDomainMax=None, polyParams=[0, 0, 0, 0, 1]):

    # Sort Arrays
    sortIndexes = np.argsort(x)
    x = [x[i] for i in sortIndexes]
    y = [y[i] for i in sortIndexes]

    # Get Fit Domain Limits
    if fitDomainMin == None:
        fitDomainMin = min(x)
    if fitDomainMax == None:
        fitDomainMax = max(x)

    # Filter X and Y Arrays
    xFiltered = []
    yFiltered = []
    for i in range(len(x)):
        if x[i] >= float(fitDomainMin) and x[i] <= float(fitDomainMax):
            xFiltered.append(float(x[i]))
            yFiltered.append(float(y[i]))
    xFiltered = np.array(xFiltered)
    yFiltered = np.array(yFiltered)

    # Fit
    fit = kmpfit.simplefit(model, [0, 0, 0, 0, 0], xFiltered, yFiltered, parinfo=[{'fixed': polyParams[0]}, {
                           'fixed': polyParams[1]}, {'fixed': polyParams[2]}, {'fixed': polyParams[3]}, {'fixed': polyParams[4]}])
    a, b, c, d, e = fit.params

    # Get Error Bands
    dfdp = [0, xFiltered, xFiltered**2, xFiltered**3, xFiltered**4]
    yFit, dyFitUpper, dyFitLower = fit.confidence_band(
        xFiltered, dfdp, 0.95, model)

    samplingIndexes = [int(x) for x in np.linspace(0, len(xFiltered)-1, 100)]
    if isinstance(xFiltered[0], (int, np.int64)):
        xFiltered = [int(x) for x in xFiltered]
    if isinstance(yFiltered[0], (int, np.int64)):
        yFiltered = [int(x) for x in yFiltered]

    xFilteredSample = [xFiltered[i] for i in samplingIndexes]
    yFilteredSample = [yFit[i] for i in samplingIndexes]
    dyFitLowerSample = [dyFitLower[i] for i in samplingIndexes]
    dyFitUpperSample = [dyFitUpper[i] for i in samplingIndexes]

    return [{'x': xFilteredSample[i], 'y': yFilteredSample[i], 'errorLower': dyFitLowerSample[i], 'errorUpper': dyFitUpperSample[i]} for i in range(len(samplingIndexes))]


def getBestDegree(x, y, fitDomainMin=None, fitDomainMax=None, maxDegree=3):

    # Min Chi-Square Array
    chiSquareArray = []

    # Sort Arrays
    sortIndexes = np.argsort(x)
    x = [x[i] for i in sortIndexes]
    y = [y[i] for i in sortIndexes]

    # Get Fit Domain Limits
    if fitDomainMin == None:
        fitDomainMin = min(x)
    if fitDomainMax == None:
        fitDomainMax = max(x)

    # Filter X and Y Arrays
    xFiltered = []
    yFiltered = []
    for i in range(len(x)):
        if x[i] >= float(fitDomainMin) and x[i] <= float(fitDomainMax):
            xFiltered.append(float(x[i]))
            yFiltered.append(float(y[i]))
    xFiltered = np.array(xFiltered)
    yFiltered = np.array(yFiltered)

    for degree in range(1, maxDegree):

        # Get Polynomial Parameters Array
        polyParams = getPolyParams(degree)
        # Fit
        fit = kmpfit.simplefit(
            model, [0, 0, 0, 0, 0], xFiltered, yFiltered, parinfo=[{'fixed': polyParams[0]}, {
                'fixed': polyParams[1]}, {'fixed': polyParams[2]}, {'fixed': polyParams[3]}, {'fixed': polyParams[4]}])
        chiSquareArray.append(fit.rchi2_min)

    return chiSquareArray.index(max(chiSquareArray)) + 1


def getHighestCountKeys(d):
    itemMaxValue = max(d.items(), key=lambda x: x[1])
    listOfKeys = list()
    # Iterate over all the items in dictionary to find keys with max value
    for key, value in d.items():
        if value == itemMaxValue[1]:
            listOfKeys.append(key)
    return listOfKeys


def model(p, x):
    a, b, c, d, e = p
    return a + b*x + c*x**2 + d*x**3 + e*x**4


def getPolyParams(degree, maxDegree=3):
    polyArray = []
    for n in range(degree+1):
        polyArray.append(0)
    for n in range(degree+2, maxDegree+3):
        polyArray.append(1)
    return polyArray


def getBestCurveFit(x, y, fitDomainMin=None, fitDomainMax=None, maxDegree=3):
    bestDegree = getBestDegree(x, y, fitDomainMin, fitDomainMax)
    fitObj = getCurveFit(x, y, fitDomainMin, fitDomainMax,
                         getPolyParams(bestDegree))
    return fitObj
