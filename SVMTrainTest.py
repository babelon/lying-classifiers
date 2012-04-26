import svmlight
import sys
import os
from text2vec import Vectors

class Datum:
    def __init__(self, name, label, features):
        self.label = label # an int, 1 or -1
        self.features = features # [(int index, float value),...]
        self.name = name # string

    def dataTuple(self):
        return (self.label,self.features)

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
    return Datum(name, label, features)

def readVectorFile(filename):
    infile = open(filename)
    toReturn = string2pysvmVector(infile.read())
    infile.close()
    return toReturn

def trainAndTest(training, test):
    #trainingNames = [x[0] for x in training] # never used, but might be someday
    trainingData = [d.dataTuple() for d in training]
    testNames = [d.name for d in test]
    testData = [d.dataTuple() for d in test]
    testLabels = [d.label for d in test]
    
    model = svmlight.learn(trainingData)
    predictions = svmlight.classify(model,testData)
    return zip(predictions, testLabels, testNames)

def kFoldTrainAndTest(docs, k):
    results = []
    for training, test in splitIntoFolds(docs, k):
        results.append(trainAndTest(training, test))
    return results


def truePositive(predicted, truth):
    return predicted > 0 and truth > 0

def falsePositive(predicted, truth):
    return predicted > 0 and truth < 0

def falseNegative(predicted, truth):
    return predicted < 0 and truth > 0

def summarizeFold(result):
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

def printSummary(results):
    k = len(results)
    summaries = [summarizeFold(x) for x in results]
    recalls = [recall(summary) for summary in summaries]
    precisions = [precision(summary) for summary in summaries]
    totalTP = sum([len(summary[0]) for summary in summaries])
    totalFP = sum([len(summary[1]) for summary in summaries])
    totalFN = sum([len(summary[2]) for summary in summaries])

    outfile = open('output-details','w')
    

    print '*******************************************'
    print ' PERFORMANCE '
    print '*******************************************'
    print ' Overall       P:', 
    print mean(precisions),
    print '(' + str(totalTP) + '/' + str(totalTP + totalFP) + ')'
    print '               R:',
    print mean(recalls),
    print '(' + str(totalTP) + '/' + str(totalTP + totalFN) + ')'
    print '==========================================='
    
    for i,summary in enumerate(summaries):
        print ' Fold ' + str(i) + ':       P:',
        print precisions[i],
        print '(' + str(len(summary[0])) + '/' + str(len(summary[0]) + len(summary[1])) + ')'
        print '               R:',
        print recalls[i],
        print '(' + str(len(summary[0])) + '/' + str(len(summary[0]) + len(summary[2])) + ')'
        print '-------------------------------------------'
        
        print >>outfile, '================ Fold ' + str(i) + ' ================'
        printDetailsToFile(outfile, results[i])

    outfile.close()

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
    
