import spacy
from lexrank import LexRank, STOPWORDS

from model.myutils.lex_summarizer import summarize


def map_cluster_to_data(cluster_assignment, listSnippet):
    max_clusters = max(cluster_assignment)

    print("# of Clusters: " + str(max_clusters))

    dict_of_clusters = dict()

    # Connect cluster label with the data
    for i in range(len(cluster_assignment)):
        dict_of_clusters.setdefault(cluster_assignment[i], []).append(listSnippet[i])

    return dict_of_clusters


def summarize_clusters(dict_of_cluster):
    dict_of_cluster_summary = {}

    for k, v in dict_of_cluster.items():
        # print("Summary of Cluster ", k)
        # summary = summarizer_nltp(v)
        # from gensim.summarization.summarizer import summarize
        from gensim.summarization import keywords
       # import wikipedia

        # Summary (0.5% of the original content).
        # summary = summarize(" ".join(v), ratio=0.25)
        # from gensim.summarization.summarizer import summarize

        # from summarizer import Summarizer
        #
        # body = 'Text body that you want to summarize with BERT'
        # body2 = 'Something else you want to summarize with BERT'
        # model = Summarizer()
        # print(model(body))
        # import smrzr
        # article = smrzr.Summarizer(v)
        # print(article.summary)

        # print(k)
        # print(v)

        summary = summarize(". ".join(v))

        # from sumy.parsers.plaintext import PlaintextParser
        # from sumy.nlp.tokenizers import Tokenizer
        # from sumy.summarizers.lex_rank import LexRankSummarizer
        #
        # documents = ". ".join(v)
        # parser = PlaintextParser.from_string(documents, Tokenizer("english"))
        # summarizer = LexRankSummarizer()
        # summary2 = summarizer(parser.document, 1)
        #
        # from summarizer import Summarizer
        # model = Summarizer(model='bert-base-uncased')
        # result = model(documents)
        # full = ''.join(result)
        # print(full)
        # print(summary2)
        ######### BERT SUMMARIZER ######################
        """
        from summarizer import Summarizer
        from summarizer.coreference_handler import CoreferenceHandler
        import en_core_web_sm
        nlp = en_core_web_sm.load()

        handler = CoreferenceHandler(greedyness=.4)
        # How coreference works:
        # >>>handler.process('''My sister has a dog. She loves him.''', min_length=2)
        # ['My sister has a dog.', 'My sister loves a dog.']

        model = Summarizer(sentence_handler=handler)
        summary = model(". ".join(v))
        # print("Percent summary")
        print(summary)

        # sentences = " ".join(v)
        """
        # print(summary)

        if not summary:
            summary = v[0]

        dict_of_cluster_summary[int(k)] = summary

    return dict_of_cluster_summary
