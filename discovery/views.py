from __future__ import print_function

import collections
import json
import uuid
from urllib.request import urlopen

from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.template.response import TemplateResponse

# from research.templatetags.research_extras import all_snippets
from research.data.misc_utils import get_advanced_query, get_date_parameter, format_for_gallery

from research.data.sesson_keys import SESSION_FULL_TEXT_SEARCH, SESSION_VALUE_CHANGED, SESSION_ENGINE_SEARCH, \
    SESSION_SDATE_SEARCH, SESSION_EDATE_SEARCH, SESSION_BOOL_AND_SEARCH, SESSION_BOOL_NOT_SEARCH, \
    SESSION_BOOL_OR_SEARCH, SESSION_LOC_SEARCH, SESSION_IS_CHANGED_KEY, SESSION_VALUE_NOT_CHANGED
from model.myutils.clustering_utils import map_cluster_to_data, summarize_clusters
from model.myutils.data_utils import get_sentences, map_cluster_to_data_expanded, map_cluster_to_doc_expanded
from model.myutils.graph_builder import build_doc_graph, connect_mm_doc_to_clusters, expand_view
from model.myutils.my_files_utils import save_json, read_json

from model.research.clusters import get_agg_clust_assignment
from model.research.embeddings import get_sentence_embedding, search_through_embeddings, get_snip_view
from model.research.results_aggregate import get_all_vertical_results


from django.http import HttpResponse
from django.views.decorators.clickjacking import xframe_options_exempt

@xframe_options_exempt
def index(request):
# Set a unique UUID to each visiter (used to when deylpoing multiple instances deployed)
    if request.session.get('uid', None) is None:
        request.session['uid'] = str(uuid.uuid4())

    # Filtration options (Initially empty, only set upon the user demand)
    full_text_search = ""
    lookup_level = ""
    date_start = ""
    date_end = ""
    search_engine = ""
    boolean_and = ""
    boolean_or = ""
    boolean_not = ""
    location = ""

    parameters = dict() #to encapsulate all filter options into a single dictionary

    request.session[SESSION_IS_CHANGED_KEY] = SESSION_VALUE_NOT_CHANGED #initially redner the default view

    if 'ft_search' in request.GET: #get the user entered query
        full_text_search = request.GET['ft_search']

        #check if user entered the same query. If so, retireved the cached results, else fetch new results
        if request.session.get(SESSION_FULL_TEXT_SEARCH, SESSION_VALUE_CHANGED) != full_text_search:
            request.session[SESSION_FULL_TEXT_SEARCH] = full_text_search
            request.session[SESSION_IS_CHANGED_KEY] = SESSION_VALUE_CHANGED

    if 'lookup' in request.GET: # check which view to render e.g. (lookup, eploratory, discovery, visualization)
        lookup_level = request.GET['lookup']

    if 'engine' in request.GET: # sets the source of the search engine for results retireval
        search_engine = request.GET['engine'].lower()
        parameters['engine'] = search_engine

        #update the session variable to relfec the latest search engine preference
        if request.session.get(SESSION_ENGINE_SEARCH, SESSION_VALUE_CHANGED) != search_engine:
            request.session[SESSION_ENGINE_SEARCH] = search_engine
            request.session[SESSION_IS_CHANGED_KEY] = SESSION_VALUE_CHANGED
    else: #defaul, Google will be used
        search_engine = 'google'
        parameters['engine'] = search_engine

    
    # format the user filter options suitable for the API calls
    if 'sdate' in request.GET and 'edate' in request.GET:
        date_start = request.GET['sdate']
        date_end = request.GET['edate']

        if request.session.get(SESSION_SDATE_SEARCH, SESSION_VALUE_CHANGED) != date_start:
            request.session[SESSION_SDATE_SEARCH] = date_start
            request.session[SESSION_EDATE_SEARCH] = date_end
            request.session[SESSION_IS_CHANGED_KEY] = SESSION_VALUE_CHANGED

        if search_engine == '' or search_engine == 'google':
            parameters['tbs'] = get_date_parameter(date_start, date_end, search_engine)
        else:
            parameters['freshness'] = get_date_parameter(date_start, date_end, search_engine)

    if 'andInput' in request.GET:
        boolean_and = request.GET['andInput']

        if request.session.get(SESSION_BOOL_AND_SEARCH, SESSION_VALUE_CHANGED) != boolean_and:
            request.session[SESSION_BOOL_AND_SEARCH] = boolean_and
            request.session[SESSION_IS_CHANGED_KEY] = SESSION_VALUE_CHANGED

    if 'orInput' in request.GET:
        boolean_or = request.GET['orInput']

        if request.session.get(SESSION_BOOL_OR_SEARCH, SESSION_VALUE_CHANGED) != boolean_or:
            request.session[SESSION_BOOL_OR_SEARCH] = boolean_or
            request.session[SESSION_IS_CHANGED_KEY] = SESSION_VALUE_CHANGED

    if 'notInput' in request.GET:
        boolean_not = request.GET['notInput']

        if request.session.get(SESSION_BOOL_NOT_SEARCH, SESSION_VALUE_CHANGED) != boolean_not:
            request.session[SESSION_BOOL_NOT_SEARCH] = boolean_not
            request.session[SESSION_IS_CHANGED_KEY] = SESSION_VALUE_CHANGED

    if 'loc' in request.GET:
        location = request.GET['loc']

        if search_engine == '' or search_engine == 'google':
            parameters['cr'] = 'country' + location
        else:
            parameters['loc'] = location

        if request.session.get(SESSION_LOC_SEARCH, SESSION_VALUE_CHANGED) != location:
            request.session[SESSION_LOC_SEARCH] = location
            request.session[SESSION_IS_CHANGED_KEY] = SESSION_VALUE_CHANGED

    # if new filter option set, retrieve the new resultset:
    if request.session.get(SESSION_IS_CHANGED_KEY, SESSION_VALUE_NOT_CHANGED) == SESSION_VALUE_CHANGED:
        # search_engine = 'qwant'

        parameters['q'] = get_advanced_query(boolean_and, boolean_or, boolean_not, full_text_search)

        parameters_str = ''

        for k, v in parameters.items():
            if k == 'q':
                parameters_str = v + parameters_str
            elif k == 'loc':
                parameters_str = k + ':' + v
            elif k == 'engine':
                print('hehe')
            else:
                parameters_str = '&' + k + '=' + v

        query = parameters_str

        # retireve the 100 search results from all the verticals (image, text, video, news) based on the user query
        search_results = get_all_vertical_results(query=query, num=100,
                                                  engine=search_engine)  # Initiate search results in real time
        search_results_sentences = get_sentences(
            search_results)  # Combine all the vailable text for embeddings with preprocessing
        search_result_sentence_embeddings = get_sentence_embedding(
            search_results_sentences)  # Get search results embeddings

        snip_view_process = get_snip_view(query, search_result_sentence_embeddings,
                                          search_results, request.session.get('uid', 'default'))  # save the snip view ordered by cosine relevancy

        # perform agg clustering
        search_results_cluster_assignment = get_agg_clust_assignment(search_result_sentence_embeddings,
                                                                     15)  # [1, 2,23...]
        # replace cluster assignment to data: clust1 -> snippet 1, 2, .....
        bucket_cluster_assignment_sentences = map_cluster_to_data(search_results_cluster_assignment,
                                                                  search_results_sentences)
        # bind cluster assignment to the data snippet1 -> url, date, cluster_assignment
        assigned_search_results_cluster = map_cluster_to_data_expanded(search_results_cluster_assignment,
                                                                       search_results)
        # get each cluster summary: clust [2]-> summary, clust [3]-> summary
        summarized_clusters = summarize_clusters(bucket_cluster_assignment_sentences)

        # Build MM Docs
        G = build_doc_graph(assigned_search_results_cluster, summarized_clusters)

        # get mm docs
        mm_doc_sentences = list()
        od = collections.OrderedDict(sorted(summarized_clusters.items()))
        for k, item in od.items():
            mm_doc_sentences.append(item)

        mm_doc_sentences_embeddings = get_sentence_embedding(mm_doc_sentences)

        # perform agg clust on sentences
        mm_doc_clusters = get_agg_clust_assignment(mm_doc_sentences_embeddings, 15)
        # replace cluster assignment to data: clust [1] -> snippet 1, 2, .....
        bucket_of_mm_doc_cluster = map_cluster_to_data(mm_doc_clusters, mm_doc_sentences)
        # For Summarization
        summarized_mm_doc_clusters = summarize_clusters(bucket_of_mm_doc_cluster)
        # bind cluster assignment to the data mm_doc_1 -> cluster_assignment
        expanded_dict_of_mm_clusters = map_cluster_to_doc_expanded(mm_doc_clusters, od)

        # replace cluster with summary data
        # building graph
        G = connect_mm_doc_to_clusters(G, expanded_dict_of_mm_clusters, summarized_mm_doc_clusters)
        expand_view(G)
        # Wait for result from all processes
        snip_view_process.join()

    # the retrieved files are stored as a JSON for each view (for caching and optimization purposes). This JSON is also used to build graph visualization system
    clust_view = read_json('clust_view')
    doc_view = read_json('doc_view')
    snip_view = read_json('snip_view')

    wikilook = ""
    # Change view depending on the granularity selected
    if lookup_level == 'doc':
        return render(request, 'content_doc.html',
                      {'clusters': clust_view, 'documents': doc_view, 'snippets': snip_view})
    elif lookup_level == 'snip': # if lookup view, also extract entities to display knowledge card
        snip_view = format_for_gallery(snip_view) # display successive images as a grid
        # full_text_search = "Mcdonald"

        import string
        full_text_search = full_text_search.translate(str.maketrans('', '', string.punctuation))
        import spacy
        sp = spacy.load('en_core_web_sm')
        sen = sp(full_text_search)

        lookup = ""

        for word in sen:
            if word.pos_ == "NOUN" or word.pos_ == "PROPN":
                lookup = lookup + word.text + " "

        # from textblob import TextBlob
        # wiki = TextBlob(full_text_search)
        # print(wiki.noun_phrases)
        lookup = lookup.split(' ')[0]

        try:
            import requests
            response = requests.get("http://en.wikipedia.org/w/api.php?action=query&prop=description&titles=" +
                                     lookup +
                                     "&prop=extracts&exintro&explaintext&format=json&redirects&callback=?")

            # summary = response.json()
            test = response.content.decode("UTF-8")
            test = test[5:len(test) - 1]
            j = json.loads(test)
            y = j['query']['pages'].popitem()
            wikilook = y[1]['extract']

            wikilook = {
                'query': lookup,
                'content': wikilook.replace('. ', '.<br><br>')
            }
        finally:
            if wikilook:
                return render(request, 'content_snip.html',
                          {'clusters': clust_view, 'documents': doc_view, 'snippets': snip_view, 'wiki': wikilook})
            else:
                return render(request, 'content_snip.html',
                          {'clusters': clust_view, 'documents': doc_view, 'snippets': snip_view})
    else:
        return render(request, 'content.html', {'clusters': clust_view, 'documents': doc_view, 'snippets': snip_view}) #default, discovery view will be loaded

#called ASync. and is used to display explore more panel on demand
def get_document_preview(request):
    doc_id = request.GET['doc_id']
    doc_view = read_json('doc_view')
    snip_view = read_json('snip_view')
    snip_list = doc_view[doc_id]['snips_list']

    snippets = []
    for snip_id in snip_list:
        snippets.append(snip_view[snip_id])

    return TemplateResponse(request, 'doct_preview.html',
                            {'doc_id': doc_id, 'documents': doc_view, 'snippets': snip_view, 'snip_list': snippets})


def homepage(request):
    return render(request, 'start_page.html', {})

#Minor observations that can be enhanced
# Hide explore more cluster when it is empty
# Case 1: When it is all empty including no further multimedia documents to explore
# Case2: When only explore more cluster is empty yet there are multimedia documents further to explore
