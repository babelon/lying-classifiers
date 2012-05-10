import sys
import os

pivot = 0
    
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

def setClassifier(x):
    global classifier
    classifier = x

def trainAndTest(training, test):
    #trainingNames = [x[0] for x in training] # never used, but might be someday

    trainingData = [(d.features,d.cat) for d in training]
    testNames = [d.name for d in test]
    testData = [(d.features,d.cat) for d in test]
    testLabels = [d.cat for d in test]

    if classifier.__name__ == 'svmlight':
        (trainingData, testData) = convertToPysvm((trainingData, testData))
    
        model = classifier.learn(trainingData)
        predictions = classifier.classify(model, testData)
        return zip(predictions, testLabels, testNames)

    else:
        model = classifier.train(trainingData)
        predictions = [model.prob_classify(t[0]).max() for t in testData]
        return zip(predictions, testLabels, testNames)



def kFoldTrainAndTest(docs, k, balanced=True):
    results = []
    combinedResult = []
    folds = []
    if not balanced:
        folds = splitIntoFolds(docs,k)
    if balanced:
        posDocs = [d for d in docs if d.cat==1]
        negDocs = [d for d in docs if d.cat==-1]
        posFolds = [(train,test) for train,test in splitIntoFolds(posDocs,k)]
        negFolds = [(train,test) for train,test in splitIntoFolds(negDocs,k)]
        for i,fold in enumerate(posFolds):
            train = fold[0]
            train.extend(negFolds[i][0])
            test = fold[1]
            test.extend(negFolds[i][1])
            folds.append((train,test))
            
    for training, test in folds:
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

    return combinedResult

def truePositive(predicted, truth):
    return predicted > pivot and truth > 0

def falsePositive(predicted, truth):
    return predicted > pivot and truth < 0

def falseNegative(predicted, truth):
    return predicted < pivot and truth > 0

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
    norm = float(len(summary[0]) + len(summary[1]))
    if norm == 0: norm = 0.0000001
    return len(summary[0]) / norm

def recall(summary):
    norm = float(len(summary[0]) + len(summary[2]))
    if norm == 0: norm = 0.0000001
    return len(summary[0]) / norm

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
    print '  n=',str(len(result))
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
    





def convertToPysvm(dtuple):
    features = set()
    for docs in dtuple: # training and test
        for d in docs: # a (features,cat) tuple
            for f in d[0]: # a key in features
                features.add(f)
    featureIndices = {f : i for i, f in enumerate(features)}
    toReturn = []
    for docs in dtuple: # training and test
        data = [] 
        for d in docs: # a (features,cat) tuple
            data.append((d[1],makePysvmVector(d[0],featureIndices)))
        toReturn.append(data)
    return tuple(toReturn)

def makePysvmVector(features, featureIndices):
    toReturn = []
    docFeatureIndices = []
    docFeatureValues = dict()
    for f in features:
        docFeatureIndices.append(featureIndices[f])
        docFeatureValues[featureIndices[f]] = features[f]
    for i in qsort(docFeatureIndices):
        toReturn.append((i,docFeatureValues[i]))
    return toReturn


def qsort(l):
    """                                                                                                                                   
    Quicksort using list comprehensions                                                                                                   
    >>> qsort1<<docstring test numeric input>>                                                                                            
    <<docstring test numeric output>>                                                                                                     
    >>> qsort1<<docstring test string input>>                                                                                             
    <<docstring test string output>>                                                                                                      
    """
    if l == []:
        return []
    else:
        pivot = l[0]
        lesser = qsort([x for x in l[1:] if x < pivot])
        greater = qsort([x for x in l[1:] if x >= pivot])
        return lesser + [pivot] + greater
    
