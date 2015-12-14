import pickle
import pandas as pd
import re
from gensim.models.doc2vec import LabeledSentence
import gensim

print "Loading features and labels"
features = pickle.load(open("features.p","rb"))
labels_list = pickle.load(open("labels_list.p","rb"))

# From https://medium.com/@klintcho/doc2vec-tutorial-using-gensim-ab3ac03d3a1
class LabeledLineSentence(object):
    def __init__(self, doc_list, labels_list):
        self.labels_list = labels_list
        self.doc_list = doc_list
    def __iter__(self):
        for idx, doc in enumerate(self.doc_list):
            yield LabeledSentence(words=doc,tags=[self.labels_list[idx]])

print "Build vocab"
# Generate vocab
it = LabeledLineSentence(features, labels_list)
# Use 300 nodes, context window of 20, minimum word count of 5, 11 threads, 0.025 for learning rate
# DM model/ CBOW and compute word vectors along with doc vectors

model = gensim.models.Doc2Vec(size=300, window=20,
                              min_count=5, workers=11,alpha=0.025, min_alpha=0.025,
                             dm=1) # use fixed learning rate
model.build_vocab(it)

print "Training model..."
for epoch in range(10):
    model.train(it)
    model.alpha -= 0.002 # decrease the learning rate
    model.min_alpha = model.alpha # fix the learning rate, no deca
    model.train(it)
    print "Iteration", epoch+1

print "Training complete"

print "Saving Model"

model.save("doc2vec_dm_NAEUR.model")
