import sys
import os
from text2vec import Vectors

def makeVectorsFromFiles(pathname, outdir, **params):
    v = Vectors(**params)
    for docName in os.listdir(pathname):
    #print "Adding document " + docName
        docFile = open(pathname+docName,'r')
        docText = docFile.read()
        if len(docText) > 0:
            v.addText(docText,docName)
        docFile.close()
            
    if not os.path.exists(outdir):
        os.makedirs(outdir)
                
    for docName in v.docs:
        outfile = open(outdir+docName,'w')
        print >>outfile, v.vectorString(v.docs[docName])
        outfile.close()

    v.saveFeatures()
