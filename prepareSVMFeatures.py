import sys
from text2vec import Vectors

userInput = sys.argv[1:]
v = Vectors()
for docName in userInput:
    #docName = "op_spam_v1.3/all/" + docName
    #print "Adding document " + docName
    docText = [s for s in open(docName)]
    if len(docText) > 0:
        docText = docText[0]
        v.addDoc(docName,docText)
v.saveFeatures()

for docName in v.docs.keys():
    s = v.vectorString(v.docs[docName])
    if "d_" in s:
        print "+1 " + s
    if "t_" in s:
        print "-1 " + s

