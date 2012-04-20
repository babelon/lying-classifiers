import sys
from text2vec import Vectors

userInput = sys.argv[1:]
v = Vectors()
for docName in userInput:
    docName = "op_spam_v1.3/train/" + docName
    print "Adding document " + docName
    docText = [s for s in open(docName)]
    if len(docText) > 0:
        docText = docText[0]
        v.addDoc(docName,docText)
v.printAllVectors()
