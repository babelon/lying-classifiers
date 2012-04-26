import sys
import os
import SVMTrainTest
import produceVectors
import argparse

parser = argparse.ArgumentParser(description='k-fold cross validation of SVM classification of text files')
parser.add_argument('dir',type=str,default='op_spam_v1.3/all/',help='directory with training data',action='store')
parser.add_argument('-k','--folds',type=int,default=5,help='number of folds for k-fold cross-validation, default 5',action='store')
parser.add_argument('-n','--ngramOrder',type=int,default=3,help='ngram order, default 3',action='store')

# Main
args = parser.parse_args()
pathname = vars(args)['dir']
howManyFolds = vars(args)['folds']
ngramOrder = vars(args)['ngramOrder']

if not pathname[-1] == '/':
    pathname += '/'


###### CONVERT FILES TO FEATURE VECTORS ######                                 
outdir = 'vectors/'
params = dict()
params['ngramOrder'] = ngramOrder
produceVectors.makeVectorsFromFiles(pathname, outdir, **params)

###### TRAIN & TEST AN SVM #####                                              
pathname = outdir
files = os.listdir(pathname)
vectors = [SVMTrainTest.readVectorFile(pathname+f) for f in files]
results = SVMTrainTest.kFoldTrainAndTest(vectors, howManyFolds)

SVMTrainTest.printSummary(results)
