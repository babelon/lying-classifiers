import re
import os
from tok import Tokenizer #insert your favorite tokenizer here
import nltk
from collections import Counter

tok = Tokenizer()

def dir2docs(pathname, **kwargs):
    docs = []
    for filename in os.listdir(pathname):
        docs.append(file2doc(filename,pathname,**kwargs))
    return docs

def file2doc(filename, pathname='', **kwargs):
    infile = open(pathname+filename)
    toReturn = string2doc(infile.read(),filename, **kwargs)
    infile.close()
    return toReturn

def string2doc(string, name, **kwargs):
    tokens = tok.tokenize(string)
    return document(name, tokens, **kwargs)

class document:
    # A document representation:
    # 1. A name, 'name'
    # 2. A category, 'cat'
    # 3. a dictionary of features and their values, 'features'
    def __init__(self, docName, docTokens, **kwargs):

        self.name = docName
        self.features = dict()
        self.cat = 0

        self.params = dict()
        # set defaults
        self.params['ngramOrder'] = 3
        self.params['posCat'] = '^d_'
        self.params['negCat'] = '^t_'
        self.params['posgramOrder'] = 0

        # read user-specified args
        for arg in kwargs:
            self.params[arg] = kwargs[arg]

        posCat = re.compile(self.params['posCat'])
        negCat = re.compile(self.params['negCat'])
        self.cat = self.identifyClass(docName, posCat, negCat)

        if 'ngramOrder' not in self.params:
            self.params['ngramOrder'] = 0
        if 'posgramOrder' not in self.params:
            self.params['posgramOrder'] = 0

        for i in xrange(self.params['ngramOrder']):
            self.addFeatures(self.grams(docTokens,i+1))

        if self.params['posgramOrder'] > 0:
            tags = [x[1] for x in nltk.pos_tag(docTokens)]
            for i in xrange(self.params['posgramOrder']):
                self.addFeatures(self.grams(tags,i+1))

        self.addRatingFeature(docName)

    def identifyClass(self, name, posCat, negCat):
        if posCat.match(name):
            return 1
        if negCat.match(name):
            return -1
        print "Warning! Could not identify true category of " + name
        return 0

    def addRatingFeature(self, docName):
        if '_r1' in docName:
            self.addFeatures({'RATING':1})
        if '_r2' in docName:
            self.addFeatures({'RATING':2})
        if '_r3' in docName:
            self.addFeatures({'RATING':3})
        if '_r4' in docName:
            self.addFeatures({'RATING':4})
        if '_r5' in docName:
            self.addFeatures({'RATING':5})

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
        """Take a dict of feature:value pairs and add those features."""
        for f in features:
            if f in self.features:
                self.features[f] += features[f]
            else:
                self.features[f] = features[f]
            

    def grams(self, tokens, n):
        if n == 1:
            return Counter(tokens)
        if n == 2:
            if len(tokens) > 1:
                return Counter(zip(tokens[0:],tokens[1:]))
            else:
                return self.grams(tokens,1)
        if n == 3:
            if len(tokens) > 2:
                return Counter(zip(tokens[0:],tokens[1:],tokens[2:]))
            else:
                return self.grams(tokens,2)
        if n == 4:
            if len(tokens) > 3:
                return Counter(zip(tokens[0:],tokens[1:],tokens[2:],tokens[3:]))
            else:
                return self.grams(tokens,2)
