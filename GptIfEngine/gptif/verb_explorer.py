import nltk
from nltk.corpus import verbnet

print(verbnet.classids(lemma="sit"))
print(verbnet.classids(lemma="kneel"))
print(verbnet.classids(lemma="lie"))


from nltk.corpus import wordnet

print([x.hypernym_paths() for x in wordnet.synsets("gangway")])
