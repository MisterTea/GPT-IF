import nltk

nltk.download("verbnet")
nltk.download("wordnet")

from nltk.corpus import verbnet

# print(verbnet.classids(lemma="persuade"))
# print(verbnet.classids(lemma="ask"))
# print(verbnet.classids(lemma="tell"))


from nltk.corpus import wordnet

print([x.hypernym_paths() for x in wordnet.synsets("pool")])
