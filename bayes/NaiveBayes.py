import re, math, json

class NaiveBayes:
  def __init__(self,filename=None):
    # Counts of feature/category combinations
    self.fc={}
    # Counts of documents in each category
    self.cc={}
    self.thresholds={}
    self.default_threshold = 1

  def load_data(self,data_file):
    with open(data_file, "r") as f:
      (self.fc, self.cc) = json.load( f )
  def save_data(self,data_file):
    with open(data_file,"w") as f:
      json.dump( (self.fc, self.cc), f )

  def incf(self,feature,cat):
    try:
      self.fc[cat][feature] += 1
    except KeyError:
      try:
        self.fc[cat][feature] = 1
      except KeyError:
        self.fc[cat] = {}
        self.fc[cat][feature] = 1

  def fcount(self,feature,cat):
    try:
      result = self.fc[cat][feature]
    except KeyError:
      result = 0;
    return result

  def incc(self,cat):
    try:
      self.cc[cat] += 1
    except KeyError:
      self.cc[cat] = 1

  def catcount(self,cat):
    try:
      result = self.cc[cat]
    except KeyError:
      result = 0
    return result

  def categories(self):
    return [d for d in self.cc]

  def totalcount(self):
    return sum([ self.cc[cat] for cat in self.cc ])

  def train(self,features,cat):
    for f in features:
      self.incf(f,cat)
    # Increment the count for this category
    self.incc(cat)

  def fprob(self,f,cat):
    if self.catcount(cat)==0: return 0

    # The total number of times this feature appeared in this 
    # category divided by the total number of items in this category
    return self.fcount(f,cat)/self.catcount(cat)

  def weightedprob(self,f,cat,prf,weight=1.0,ap=0.5):
    # Calculate current probability
    basicprob=prf(f,cat)

    # Count the number of times this feature has appeared in
    # all categories
    totals=sum([self.fcount(f,c) for c in self.categories()])

    # Calculate the weighted average
    bp=((weight*ap)+(totals*basicprob))/(weight+totals)
    #print ("DEBUG:word={} /  basicprob={} / totals={} / bp={}".format(f,basicprob,totals,bp))
    return 5*bp

  def docprob(self,features,cat):
    # Multiply the probabilities of all the features together
    p=1
    for f in features: p*=self.weightedprob(f,cat,self.fprob)
    return p

  def prob(self,features,cat):
    catprob=self.catcount(cat)/self.totalcount()
    docprob=self.docprob(features,cat)
    result = docprob*catprob
    #print ("Probability for {} : {}".format( cat, result ) )
    return result

  def setthreshold(self,cat,t):
    self.thresholds[cat]=t

  def getthreshold(self,cat):
    if cat not in self.thresholds: return self.default_threshold
    return self.thresholds[cat]

  def classify(self,features,default=None):
    probs={}
    # Find the category with the highest probability
    max=0.0
    #We filter out words not in the filter data to avoid very low probability for long articles
    real_features = []
    for f in features:
      for cat in self.fc:
        if f in self.fc[cat]:
          real_features.append(f)
          break
    for cat in self.categories():
      probs[cat]=self.prob(real_features,cat)
      if probs[cat]>max:
        max=probs[cat]
        best=cat
    interest = (probs["interesting"]/probs["not-interesting"])

    # Make sure the probability exceeds threshold*next best
    for cat in probs:
      if cat==best: continue
      if probs[cat]*self.getthreshold(best)>probs[best]: return (default, interest)
    return (best, interest)

