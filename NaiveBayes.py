from collections import Counter 
from math import log

class NaiveBayesModel:
    def __init__(self):
        self.classes = dict() #class (1 or -1) -> ClassModel
        self.classes[1] = ClassModel()
        self.classes[-1] = ClassModel()
    
    def getPrior(self, c):
        priorCount = self.classes[c].priorCount
        priorNorm = sum([self.classes[c].priorCount for c in self.classes])
        return log(priorCount) - log(priorNorm)

    def getFeatures(self, c):
        counts = self.classes[c].featureCounts
        norm = self.classes[c].featureNorm
        return Counter({x:(log(counts[x]) - log(norm)) for x in counts})

    def getFeature(self, c,f):
        featureCount = self.classes[c].featureCounts[f]
        norm = self.classes[c].featureNorm
        return log(featureCount) - log(norm)

    def updatePrior(self, c, count=1):
        self.classes[c].priorCount += count

    def addFeature(self, c, feature, val=1):
        self.classes[c].addFeature(feature,val)

class ClassModel:

    def __init__(self):
        self.priorCount = 0
        self.featureCounts = Counter()
        self.featureNorm = 0

    def addFeature(self, feature, val):
        self.featureCounts[feature] += val
        self.featureNorm += val

def learn(data):
    """Learn from training examples and output a Model."""
    model = NaiveBayesModel()
    for doc in data:
        learnDocument(model, doc)
    return model

def learnDocument(model, doc):
    c = doc[0]
    model.updatePrior(c)
    features = doc[1]
    for feature, value in features:
        model.addFeature(c, feature, value)

def classify(model, data):
    return [classifyDocument(model, doc) for doc in data]

def classifyDocument(model, doc):
    results = []
    for c in model.classes:
        result = -1*-model.getPrior(c) #prior
        result += -1*-sum(likelihoods(model,doc[1],c))
        result *= int(c) #mark class
        results.append(result)
    return results[argmin([abs(x) for x in results])]

def argmin(x):
    return x.index(min(x))

def argmax(x):
    return x.index(max(x))

def likelihoods(model, features, c):
    modelFeatures = model.getFeatures(c)
    probs = [modelFeatures[f]+log(val) for f,val in features]
    print probs
    return normalize(probs)

def normalize(probs):
    norm = float(sum(probs))
    if norm == 0: norm = 1
    return [x/norm for x in probs]
