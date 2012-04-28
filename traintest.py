#!/usr/bin/env python

import sys
import os
import SVMTrainTest
import produceVectors
from text2vec import Vectors
import argparse

parser = argparse.ArgumentParser(description='k-fold cross validation of SVM classification of text files')
parser.add_argument('dir',type=str,default='op_spam_v1.3/all/',help='directory with training data',action='store')
parser.add_argument('-k','--folds',type=int,default=5,help='number of folds for number of folds for cross-validation, default 5',action='store')
parser.add_argument('-n','--ngramOrder',type=int,default=3,help='ngram order, default 3',action='store')
parser.add_argument('-p','--printVectors',type=str,default='',help='directory to print vector representations of documents into. By default, vectors are not printed.',action='store')

# Main
args = parser.parse_args()
pathname = vars(args)['dir']
howManyFolds = vars(args)['folds']
ngramOrder = vars(args)['ngramOrder']
outdir = vars(args)['printVectors']
if not pathname[-1] == '/':
    pathname += '/'


###### CONVERT FILES TO FEATURE VECTORS ######                                 

params = dict()
params['ngramOrder'] = ngramOrder
vectors = []
if not outdir == '':
    if not outdir[-1] == '/':
        outdir += '/'

    produceVectors.makeVectorsFromFiles(pathname, outdir, **params)
    pathname = outdir
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

###### TRAIN & TEST AN SVM #####                                              
results = SVMTrainTest.kFoldTrainAndTest(vectors, howManyFolds)
