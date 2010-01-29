

from wpTextExtractor import wiki2sentences
import wikipydia
import nltk

sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')

t=wikipydia.query_text_raw('Barack Obama')['text']
sents= wiki2sentences(t,sent_detector)

for s,t in zip(*sents):
    print t,s
