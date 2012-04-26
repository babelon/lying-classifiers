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
            v.addDoc(docName,docText)
            docFile.close()
            
    if not os.path.exists(outdir):
        os.makedirs(outdir)
                
    for docName in v.docs.keys():
        s = v.vectorString(v.docs[docName])
        outfile = open(outdir+docName,'w')
                    
        if "# d_" in s: # GENERALIZE THIS TO A REGEX?
            print >>outfile, "+1 " + s
        if "# t_" in s:
            print >>outfile, "-1 " + s
            
        outfile.close()
    v.saveFeatures()
