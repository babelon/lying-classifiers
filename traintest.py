import sys
import os
import validateSVM
import produceVectors

# Main  
howManyFolds = int(sys.argv[2])
pathname = sys.argv[1]
if not pathname[-1] == '/':
    pathname += '/'

###### CONVERT FILES TO FEATURE VECTORS ######                                                               
outdir = 'vectors/'
produceVectors.makeVectorsFromFiles(pathname, outdir)

###### TRAIN & TEST AN SVM #####                                                                             
pathname = outdir
files = os.listdir(pathname)
vectors = [validateSVM.readVectorFile(pathname+f) for f in files]
results = validateSVM.kFoldTrainAndTest(vectors, howManyFolds)

validateSVM.printSummary(results)
