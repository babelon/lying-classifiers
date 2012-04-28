import svmlight as svm
import sys
import os
from text2vec import Vectors

## {{{ http://code.activestate.com/recipes/521906/ (r3)
def splitIntoFolds(X, K, randomise=False):
    """Generates K (training, validation) pairs from the items in X.
    
    The validation iterables are a partition of X, and each validation
    iterable is of length len(X)/K. Each training iterable is the
    complement (within X) of the validation iterable, and so each training
    iterable is of length (K-1)*len(X)/K.
    """

    if randomise: from random import shuffle; X=list(X); shuffle(X)
    for k in xrange(K):
        training = [x for i, x in enumerate(X) if i % K != k]
        validation = [x for i, x in enumerate(X) if i % K == k]
        yield training, validation
## end of http://code.activestate.com/recipes/521906/ }}}

def string2pysvmVector(string):
    string = [s.strip() for s in string.split('#')]
    name = string[1].strip()
    string = string[0].split(' ')
    label = int(string[0])
    features = []
    for feature in string[1:]:
        index, value = feature.split(':')
        features.append((int(index),float(value)))
    return (name, label, features)

def readVectorFile(filename):
    infile = open(filename)
    toReturn = string2pysvmVector(infile.read())
    infile.close()
    return toReturn

def trainAndTest(training, test):
    #trainingNames = [x[0] for x in training] # never used, but might be someday
    trainingData = [(d[1],d[2]) for d in training]

    testNames = [d[0] for d in test]
    testData = [(d[1],d[2]) for d in test]
    testLabels = [d[1] for d in test]
    
    model = svm.learn(trainingData)
    predictions = svm.classify(model,testData)
    return zip(predictions, testLabels, testNames)

def kFoldTrainAndTest(docs, k):
    results = []
    combinedResult = []
    for training, test in splitIntoFolds(docs, k):
        result = trainAndTest(training,test)
        results.append(result)
        for i in xrange(len(result)):
            combinedResult.append(result[i])


    print '**************************************'
    print '            PERFORMANCE'
    print '**************************************'
    print ' Overall:'
    printSummary(combinedResult)

    outfile = open('output-details','w')
    for i, result in enumerate(results):
        print '=========== Fold ' + str(i) + ' ==========='
        printSummary(result)

        print >>outfile,'=========== Fold ' + str(i) + ' ==========='
        printDetailsToFile(outfile,result)
    outfile.close()

    return results

def truePositive(predicted, truth):
    return predicted > 0 and truth > 0

def falsePositive(predicted, truth):
    return predicted > 0 and truth < 0

def falseNegative(predicted, truth):
    return predicted < 0 and truth > 0

def summarize(result):
    # result is a list of docs
    # doc is a triple: (predicted, true label, filename)
    truePositives = [doc[2] for doc in result if truePositive(doc[0],doc[1])]
    falsePositives = [doc[2] for doc in result if falsePositive(doc[0],doc[1])]
    falseNegatives = [doc[2] for doc in result if falseNegative(doc[0],doc[1])]

    # a summary is a triple (tp, fp, fn)
    # tp, fp, and fn are lists
    return (truePositives, falsePositives, falseNegatives)

def precision(summary):
    return float(len(summary[0])) / float((len(summary[0]) + len(summary[1])))

def recall(summary):
    return float(len(summary[0])) / float((len(summary[0]) + len(summary[2])))

def removeSign(number):
    return sign(number) * number

def sign(number):
    """Will return 1 for positive,
    -1 for negative, and 0 for 0"""
    try:return number/abs(number)
    except ZeroDivisionError:return 0

def mean(l):
    return float(sum(l)) / float(len(l))

def printSummary(result):
    summary = summarize(result)
    print '  P:', 
    print precision(summary),
    print '(' + str(len(summary[0])) + '/' + str(len(summary[0]) + len(summary[1])) + ')'
    print '  R:',
    print recall(summary),
    print '(' + str(len(summary[0])) + '/' + str(len(summary[0]) + len(summary[2])) + ')'


def printDetailsToFile(outfile, result):
    for resultDoc in result:
        print >>outfile, removeSign(resultDoc[0]), # prediction
        print >>outfile, resultDoc[1], # true category
        print >>outfile, resultDoc[2], # file name
        if truePositive(resultDoc[0],resultDoc[1]):
            print >>outfile, 'tp'
        elif falsePositive(resultDoc[0],resultDoc[1]):
            print >>outfile, 'fp'
        elif falseNegative(resultDoc[0],resultDoc[1]):
            print >>outfile, 'fn'
        else:
            print >>outfile, 'tn'
    
