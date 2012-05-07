class NaiveBayesModel:
    def __init__(self):
        self.classes = dict() #class (1 or -1) -> ClassModel
        self.classes[1] = ClassModel()
        self.classes[-1] = ClassModel()
    
    def getPrior(c):
        priorCount = classes[c].priorCount
        priorNorm = sum([self.classes[c].priorCount for c in self.classes])
        return -1*(log(priorCount) - log(priorNorm))

    def getFeatures(c):
        counts = self.classes[c].featureCounts
        priorCount = self.classes[c].priorCount
        return ((-1*(log(counts[x]) - log(priorCount))) for x in counts)

    def getFeature(c,f):
        featureCount = self.classes[c].featureCounts[f]
        return -1*(log(featureCount) - log(self.classes[c].priorCount))

    def updatePrior(c, count=1):
        self.classes[c].priorCount += count

    def addFeature(c, feature, val=1):
        self.classes[c].featureCounts[feature] += count

class ClassModel:
    priorCount = 0
    featureCounts = dict()

    def featureNorm(self):
        return sum((featureCounts[f]
 

def learn(data):
    """Learn from training examples and output a Model."""
    model = NaiveBayesModel()
    for doc in data:
        learnDocument(model, doc)
    return model

def learnDocument(model, doc):
    c = doc[0]
    features = doc[1]
    model.updatePrior(c)
    

def classify(model, data):
    return [classifyDocument(model, doc) for doc in data]

def classifyDocument(model, doc):
    results = []
    for c in model.classes:
        result = model.getPrior(c)
        result += sum(model.getFeatures(c))
        result *= int(c)
        results.append(result)
    return results[argmin([abs(x) for x in results])]

def argmin(x):
    return x.index(min(x))

def argmax(x):
    return x.index(max(x))
    
        
        
    
