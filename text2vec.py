import sys
from tok import Tokenizer

class Vectors:
    # A set of text docs and an ordered list of features
    # for describing those docs. 
    # A doc is a set of features.
    # Includes method for producing a vector of a given
    # doc,
    # and for adding a doc and its features to the class.

    def __init__(self):
        self.docs = dict()
        self.features = []
        self.tok = Tokenizer()

    def addDoc(self, docName, docString):
        # Initially doc is a string.
        doc = document(docName, self.tok.tokenize(docString)) # produces a list of tokens
        self.docs[docName] = doc
        self.addFeatures(doc)

    def addFeatures(self, doc):
        for f in doc.getFeatureSet():
            if f not in self.features:
                self.features.append(f)
        

    def vectorString(self, doc):
        s = ""
        for i in xrange(len(self.features)):
            f = self.features[i]
            if f in doc.getFeatureSet():
                s += str(i)
                s += ":"
                s += str(doc.getFeatureValue(f))
                s += " "
        s += "# "
        s += str(doc.name)
        return s
  
    def printVector(self, docName):
        print self.vectorString(self.docs[docName])
    
    def printAllVectors(self):
        for docName in self.docs.keys():
            self.printVector(docName)

    def printFeatures(self):
        for i in xrange(len(self.features)):
            print self.features[i]
            
class document:
    # A document representation:
    # A name
    # Consists of a dictionary of features and their values.
    def __init__(self, docName, docTokens):
        self.name = docName
        self.features = dict() #features->floats
        self.addFeatures(self.grams(docTokens,1))
        self.addFeatures(self.grams(docTokens,2))
        self.addFeatures(self.grams(docTokens,3))

    def getFeatureValue(self, feature):
        if feature in self.features:
            return self.features[feature]
        else: 
            return NULL

    def getFeatures(self):
        return self.features

    def getFeatureSet(self):
        return self.features.keys()
        
    def addFeatures(self, features):
        for f in features:
            if f in self.features:
                self.features[f] += features[f]
            else:
                self.features[f] = features[f]
            

    def grams(self, tokens, n):
        if n == 1:
            return self.hist(tokens)
        if n == 2:
            if len(tokens) > 1:
                return self.hist(zip(tokens[0:],tokens[1:]))
            else:
                return self.grams(tokens,1)
        if n == 3:
            if len(tokens) > 2:
                return self.hist(zip(tokens[0:],tokens[1:],tokens[2:]))
            else:
                return self.grams(tokens,2)

    def hist(self, l):
        d = {}
        for x in l:
            if x in d:
                d[x] += 1
            else:
                d[x] = 1
        return d
