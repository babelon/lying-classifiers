import sys
import re
import cPickle as pickle
from tok import Tokenizer #insert your favorite tokenizer here

class Vectors:
    # A set of text docs and an ordered list of features
    # for describing those docs. 
    # A doc is a set of features.
    # Includes method for producing a vector of a given doc,
    # and for adding a doc and its features to the class.

    def __init__(self, **kwargs):
        self.docs = dict()
        self.features = dict()
        self.featureIndex = 1
        self.tok = Tokenizer()

        self.params = dict()
        # defaults
        self.params['ngramOrder'] = 3
        self.params['posCat'] = '^d_'
        self.params['negCat'] = '^t_'

        # read user-specified args
        for arg in kwargs:
            self.params[arg] = kwargs[arg]

        # compile regexes
        self.posCatRegex = re.compile(self.params['posCat'])
        self.negCatRegex = re.compile(self.params['negCat'])
        

    def addDocFile(self, filename):
        docString = open(filename).read()
        self.addDoc(filename,docString)

    def addDoc(self, docName, docString):
        doc = document(docName, self.tok.tokenize(docString), **self.params) # produces a list of tokens
        self.docs[docName] = doc
        self.addFeatures(doc)

    def addFeatures(self, doc):
        for f in doc.getFeatureSet():
            if f not in self.features:
                self.features[f] = self.featureIndex
                self.featureIndex += 1

    def reverseDict(self, m):
        return dict((v,k) for k,v in map.iteritems())
        
    def qsort(self, l):
        """
        Quicksort using list comprehensions
        >>> qsort1<<docstring test numeric input>>
        <<docstring test numeric output>>
        >>> qsort1<<docstring test string input>>
        <<docstring test string output>>
        """
        if l == []: 
            return []
        else:
            pivot = l[0]
            lesser = self.qsort([x for x in l[1:] if x < pivot])
            greater = self.qsort([x for x in l[1:] if x >= pivot])
            return lesser + [pivot] + greater
        

    def vectorString(self, doc):
        s = ""
        vector = self.vectorList(doc)
        for (feature,value) in vector:
            s += str(feature)
            s += ":"
            s += str(value)
            s += " "
        s += "# "
        s += str(doc.name)

        if self.posCatRegex.match(doc.name):
            return '1 ' + s
        if self.negCatRegex.match(doc.name):
            return '-1 ' + s

        print "Error! " + doc.name + " could not be classified as pos or neg!"
        return ''


    def vectorList(self, doc):
        toReturn = []
        docFeatureIndices = []
        docFeatureValues = dict()
        for f in doc.getFeatureSet():
            if f in self.features:
                docFeatureIndices.append(self.features[f])
                docFeatureValues[self.features[f]] = doc.getFeatureValue(f)
        for i in self.qsort(docFeatureIndices):
            toReturn.append((i,docFeatureValues[i]))
        return toReturn

    def pysvmVector(self, doc):
        vector = self.vectorList(doc) # an ordered list of (feature,value) tuples
        if self.posCatRegex.match(doc.name):
            return (doc.name,1,vector)
        if self.negCatRegex.match(doc.name):
            return (doc.name,-1,vector)
        print "Error! Could not classify " + doc.name
        return ()

    def allPysvmVectors(self):
        vectors = []
        for docName in self.docs.keys():
            vectors.append(self.pysvmVector(self.docs[docName]))
        return vectors

    def pysvmVectorFromString(self, string, name='noName'):
        return self.pysvmVector(document(name, self.tok.tokenize(string), **self.params))

    def pysvmVectorFromFile(self, filename):
        docString = open(filename).read()
        return self.pysvmVectorFromString(docString,name=filename)

    def printVector(self, docName):
        s = self.vectorString(self.docs[docName])
        print s
    
    def printAllVectors(self):
        for docName in self.docs.keys():
            self.printVector(docName)

    def printFeatures(self):
        for f in self.features:
            print self.features[f]

    def saveFeatures(self):
        saveFile = open('dat.features','w')
        pickle.dump(self.features,saveFile)
        saveFile.close()

    def loadFeatures(self, filename):
        readFile = open(filename)
        self.features = pickle.load(readFile)
        readFile.close()

    def convertString(self, string, name='noName'):
        # Convert a string to a vector without adding it to the representation.
        print self.vectorString(document(name, self.tok.tokenize(string),**self.params))

    def convertFile(self, filename):
        docString = open(filename).read()
        self.convertString(docString,name=filename)
        
            
class document:
    # A document representation:
    # 1. A name
    # 2. a dictionary of features and their values.
    def __init__(self, docName, docTokens, **kwargs):
        self.name = docName
        self.features = dict() #features->floats
        if kwargs['ngramOrder'] > 0:
            for i in xrange(kwargs['ngramOrder']):
                self.addFeatures(self.grams(docTokens,i+1))


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
        if n == 4:
            if len(tokens) > 3:
                return self.hist(zip(tokens[0:],tokens[1:],tokens[2:],tokens[3:]))
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
