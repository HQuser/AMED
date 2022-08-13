# import string
#
# full_text_search = "is IPCC related to the global warming"
# import spacy
#
# sp = spacy.load('en_core_web_sm')
# sen = sp(full_text_search)
#
# lookup = ""
#
# for word in sen:
#     if word.pos_ == "NOUN" or word.pos_ == "PROPN":
#         lookup = lookup + word.text + " "
#
# print(word)
# from textblob import TextBlob
# wiki = TextBlob(full_text_search)
# print(wiki.noun_phrases)
# try:
#     import requests
#
#     response = requests.get("http://en.wikipedia.org/w/api.php?action=query&prop=description&titles=" +
#                             lookup +
#                             "&prop=extracts&exintro&explaintext&format=json&redirects&callback=?")
#
#     # summary = response.json()
#     test = response.content.decode("UTF-8")
#     test = test[5:len(test) - 1]
#     j = json.loads(test)
#     y = j['query']['pages'].popitem()
#     wikilook = y[1]['extract']
#
#     wikilook = {
#         'query': lookup,
#         'content': wikilook.replace('. ', '.<br><br>')
#     }
# finally:
#     if wikilook:
#         return render(request, 'content_snip.html',
#                       {'clusters': clust_view, 'documents': doc_view, 'snippets': snip_view, 'wiki': wikilook})
#     else:
#         return render(request, 'content_snip.html',
#                       {'clusters': clust_view, 'documents': doc_view, 'snippets': snip_view})
# else:
# return render(request, 'content.html', {'clusters': clust_view, 'documents': doc_view, 'snippets': snip_view})
import multiprocessing
import time


def f1(q):
    print('im function 1')
    q.put({'p1': 1})


def f2(q):
    time.sleep(2.4)
    print('im function 2')
    q.put(2)


def f3(q):
    print('im function 3')
    q.put(3)


def f4(q):
    print('im function 4')
    q.put(14)

import multiprocessing as mp

if __name__ == '__main__':
    qout = mp.Queue()
    processes = [mp.Process(target=f1, args=(qout,)),
                 mp.Process(target=f2, args=(qout,)),
                 mp.Process(target=f3, args=(qout,)),
                 mp.Process(target=f4, args=(qout,))
                 ]

    for p in processes:
        p.start()

    for p in processes:
        p.join()


    unsorted_result = [qout.get() for p in processes]
    print(unsorted_result)
    # result = [t[1] for t in sorted(unsorted_result)]
    # print(result)

    # module1.init()
    # process1 = multiprocessing.Process(target=f1)
    # process2 = multiprocessing.Process(target=f2)
    # process3 = multiprocessing.Process(target=f3)
    # process4 = multiprocessing.Process(target=f4)
    # print(process1)
    # process1.start()
    # process2.start()
    # process3.start()
    # process4.start()


    # process1.join()
    # process2.join()
    # process3.join()
    # process4.join()