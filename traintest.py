#!/usr/bin/env python

import sys
import os
import ClassifierTrainTest
import cPickle as pickle
import text2vec
import argparse
import nltk


parser = argparse.ArgumentParser(description='k-fold cross validation of SVM classification of text files')
parser.add_argument('dir',type=str,default='dbyank/',help='directory with training data',action='store')
parser.add_argument('-k','--folds',type=int,default=5,help='number of folds for number of folds for cross-validation, default 5',action='store')
parser.add_argument('-n','--ngramOrder',type=int,default=3,help='ngram order, default 3',action='store')
parser.add_argument('-p','--posgramOrder',type=int,default=0,help='ngram order, default 0',action='store')
parser.add_argument('-o','--outputVectors',type=str,default='',help='file to Output vector representations of documents into. By default, vectors are not printed.',action='store')
parser.add_argument('-v','--inputVectors',type=str,default='',help='file of Vectors to read. If no file is selected, vectors will be generated from text files in [DIR].',action='store')
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
outfilename = vars(args)['outputVectors']
infilename = vars(args)['inputVectors']
testdir = vars(args)['test']
balanced = vars(args)['balanced']
addK = vars(args)['addK']
ClassifierTrainTest.pivot = vars(args)['cutoff']
if vars(args)['classifier'] == 'nb':
    ClassifierTrainTest.setClassifier(nltk.NaiveBayesClassifier)
elif vars(args)['classifier'] == 'maxent':
    ClassifierTrainTest.setClassifier(nltk.classify.maxent.MaxentClassifier)
else:
    import svmlight
    ClassifierTrainTest.setClassifier(svmlight)
    


if not pathname[-1] == '/':
    pathname += '/'


###### CONVERT TEXT FILES TO FEATURE VECTORS ######                                 
params = dict()
params['ngramOrder'] = ngramOrder
params['posgramOrder'] = posgramOrder
vectors = []

if not infilename == '': # If already-produced Vectors file was specified
    infile = open(infilename)
    docs = pickle.load(infile)
    infile.close()

else: # If no vectors file has been specified, generate from text files

    docs = []
    for docName in os.listdir(pathname):
        docs.append(text2vec.file2doc(docName,pathname))
    if not outfilename == '': # if output file specified
        outfile = open(outfilename,'w')
        pickle.dump(docs,outfile)
        outfile.close()


###### TRAIN & TEST AN SVM #####

if not testdir == '':   # If test documents specified
    if testdir[-1] is not '/':
        testdir += '/'

    testdocs = []
    for docName in os.listdir(testdir):
        testdocs.append(text2vec.file2doc(docName, testdir))
        

    result = ClassifierTrainTest.trainAndTest(docs, testdocs)
    ClassifierTrainTest.printSummary(result)

    outfile = open('output-details','w')
    ClassifierTrainTest.printDetailsToFile(outfile,result)
    outfile.close()
    
    
else:
    results = ClassifierTrainTest.kFoldTrainAndTest(docs, howManyFolds, balanced)
