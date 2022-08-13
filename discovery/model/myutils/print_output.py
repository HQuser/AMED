from nltk import word_tokenize, PorterStemmer
from nltk.corpus import stopwords

from research.text_summarizer import summarizer_nltp


def printClustercontents(dict_of_clusters):
    for k, v in dict_of_clusters.items():
        print("Cluster: ", k)
        for i in range(len(v)):
            print(v[i])