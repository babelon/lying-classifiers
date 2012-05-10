#!/usr/bin/env python

import sys
import os
import ClassifierTrainTest
import produceVectors
from text2vec import Vectors
import argparse

def readVectorFile(filename, v):
    infile = open(filename)
    if ClassifierTrainTest.classifier.__name__ == 'svmlight':
        toReturn = v.string2pysvmVector(infile.read())
    else:
        toReturn = v.string2nltkVector(infile.read())
    infile.close()
    return toReturn

def readVectorDir(pathname):
    if pathname[-1] is not '/':
        pathname += '/'

    v = Vectors()
    v.loadFeatures('dat.features')

    files = os.listdir(pathname)
    vectors = [readVectorFile(pathname+f, v) for f in files]

def getVectors(v):
    if ClassifierTrainTest.classifier.__name__ == 'svmlight':
        return v.allPysvmVectors()
    else: 
        return v.allDocs()




parser = argparse.ArgumentParser(description='k-fold cross validation of SVM classification of text files')
parser.add_argument('dir',type=str,default='dbyank/',help='directory with training data',action='store')
parser.add_argument('-k','--folds',type=int,default=5,help='number of folds for number of folds for cross-validation, default 5',action='store')
parser.add_argument('-n','--ngramOrder',type=int,default=3,help='ngram order, default 3',action='store')
parser.add_argument('-p','--posgramOrder',type=int,default=0,help='ngram order, default 0',action='store')
parser.add_argument('-o','--outputVectors',type=str,default='',help='directory to Output vector representations of documents into. By default, vectors are not printed.',action='store')
parser.add_argument('-v','--vectors',type=str,default='',help='directory of vectors to read. If no directory is selected, vectors will be generated from text files in [DIR].',action='store')
parser.add_argument('-t','--test',type=str,default='',help='directory of documents for testing.',action='store')
parser.add_argument('-c','--cutoff',type=float,default=0,help='cutoff value for classification as fake',action='store')
parser.add_argument('-b','--balanced',type=bool,default=True,help='whether categories in folds should be balanced',action='store')
parser.add_argument('-C','--classifier',type=str,default='svm',help='what kind of classifier to use, ie svm or nb',action='store')
parser.add_argument('-K','--addK',type=float,default=.1,help='Value of K for add-K smoothing of NB classifier.',action='store')

# Main
args = parser.parse_args()
pathname = vars(args)['dir']
howManyFolds = vars(args)['folds']
ngramOrder = vars(args)['ngramOrder']
posgramOrder = vars(args)['posgramOrder']
outdir = vars(args)['outputVectors']
indir = vars(args)['vectors']
testdir = vars(args)['test']
balanced = vars(args)['balanced']
addK = vars(args)['addK']
ClassifierTrainTest.pivot = vars(args)['cutoff']
if vars(args)['classifier'] == 'nb':
    import NaiveBayes as nb
    nb.addK = addK
    ClassifierTrainTest.setClassifier(nb)


if not pathname[-1] == '/':
    pathname += '/'


###### CONVERT TEXT FILES TO FEATURE VECTORS ######                                 
params = dict()
params['ngramOrder'] = ngramOrder
params['posgramOrder'] = posgramOrder
vectors = []
if not outdir == '': # If a vector-output directory was specified
    if not outdir[-1] == '/':
        outdir += '/'

    produceVectors.makeVectorsFromFiles(pathname, outdir, **params)
    vectors = readVectorDir(pathname)

elif not indir == '': # If already-produced vector files were specified
    vectors = readVectorDir(pathname)

else:
    v = Vectors(**params)
    for docName in os.listdir(pathname):
        docFile = open(pathname+docName,'r')
        docText = docFile.read()
        if len(docText) > 0:
            v.addText(docText,docName)
        docFile.close()
    v.saveFeatures()

    vectors = getVectors(v)


###### TRAIN & TEST AN SVM #####

if not testdir == '':   # If test documents specified
    if testdir[-1] is not '/':
        testdir += '/'

    v = Vectors(**params)
    v.loadFeatures('dat.features')
    testdocs = []
    if ClassifierTrainTest.classifier.__name__ == 'svmlight':
        for docName in os.listdir(pathname):
            testdocs.append(v.file2pysvm(pathname+docName))
    else:
        for docName in os.listdir(pathname):
            testdocs.append(v.file2doc(pathname+docName))
        

    result = ClassifierTrainTest.trainAndTest(vectors, testdocs)
    ClassifierTrainTest.printSummary(result)

    outfile = open('output-details','w')
    ClassifierTrainTest.printDetailsToFile(outfile,result)
    outfile.close()
    
    
else:
    results = ClassifierTrainTest.kFoldTrainAndTest(vectors, howManyFolds, balanced)
