#!/usr/bin/env python

import sys
import os
import SVMTrainTest
import produceVectors
from text2vec import Vectors
import argparse

parser = argparse.ArgumentParser(description='k-fold cross validation of SVM classification of text files')
parser.add_argument('dir',type=str,default='dbyank/',help='directory with training data',action='store')
parser.add_argument('-k','--folds',type=int,default=5,help='number of folds for number of folds for cross-validation, default 5',action='store')
parser.add_argument('-n','--ngramOrder',type=int,default=3,help='ngram order, default 3',action='store')
parser.add_argument('-p','--posgramOrder',type=int,default=0,help='ngram order, default 0',action='store')
parser.add_argument('-o','--outputVectors',type=str,default='',help='directory to Output vector representations of documents into. By default, vectors are not printed.',action='store')
parser.add_argument('-v','--vectors',type=str,default='',help='directory of vectors to read. If no directory is selected, vectors will be generated from text files in [DIR].',action='store')
parser.add_argument('-t','--test',type=str,default='',help='directory of documents for testing.',action='store')
parser.add_argument('-c','--cutoff',type=float,default=0,help='cutoff value for classification as fake',action='store')

# Main
args = parser.parse_args()
pathname = vars(args)['dir']
howManyFolds = vars(args)['folds']
ngramOrder = vars(args)['ngramOrder']
posgramOrder = vars(args)['posgramOrder']
outdir = vars(args)['outputVectors']
indir = vars(args)['vectors']
testdir = vars(args)['test']
SVMTrainTest.pivot = vars(args)['cutoff']

if not pathname[-1] == '/':
    pathname += '/'


###### CONVERT FILES TO FEATURE VECTORS ######                                 
params = dict()
params['ngramOrder'] = ngramOrder
params['posgramOrder'] = posgramOrder
vectors = []
if not outdir == '':
    if not outdir[-1] == '/':
        outdir += '/'

    produceVectors.makeVectorsFromFiles(pathname, outdir, **params)
    pathname = outdir
    files = os.listdir(pathname)
    vectors = [SVMTrainTest.readVectorFile(pathname+f) for f in files]

elif not indir == '':
    if not indir[-1] == '/':
        indir += '/'

    pathname = indir
    files = os.listdir(pathname)
    vectors = [SVMTrainTest.readVectorFile(pathname+f) for f in files]

else:
    v = Vectors(**params)
    for docName in os.listdir(pathname):
        docFile = open(pathname+docName,'r')
        docText = docFile.read()
        if len(docText) > 0:
            v.addDoc(docName,docText)
        docFile.close()

    vectors = v.allPysvmVectors()
    v.saveFeatures()

###### TRAIN & TEST AN SVM #####

if not testdir == '':    
    if not testdir[-1] == '/':
        testdir += '/'

    v = Vectors(**params)
    v.loadFeatures('dat.features')
    testvecs = []
    for filename in os.listdir(testdir):
        docString = open(testdir+filename).read()
        testvecs.append(v.pysvmVectorFromString(docString,name=filename))

    result = SVMTrainTest.trainAndTest(vectors, testvecs)
    SVMTrainTest.printSummary(result)
    outfile = open('output-details','w')
    SVMTrainTest.printDetailsToFile(outfile,result)
    outfile.close()
    
    
else:
    results = SVMTrainTest.kFoldTrainAndTest(vectors, howManyFolds)
