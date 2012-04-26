import sys
import os
import SVMTrainTest
import produceVectors

# Main  
howManyFolds = int(sys.argv[2])
pathname = sys.argv[1]
if not pathname[-1] == '/':
    pathname += '/'
params = dict()

###### CONVERT FILES TO FEATURE VECTORS ######                                                               
outdir = 'vectors/'
produceVectors.makeVectorsFromFiles(pathname, outdir, **params)

###### TRAIN & TEST AN SVM #####                                                                             
pathname = outdir
files = os.listdir(pathname)
vectors = [SVMTrainTest.readVectorFile(pathname+f) for f in files]
results = SVMTrainTest.kFoldTrainAndTest(vectors, howManyFolds)

SVMTrainTest.printSummary(results)
