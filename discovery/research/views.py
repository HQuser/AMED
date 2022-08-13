from __future__ import print_function

import collections
import json
import uuid
from urllib.request import urlopen

import networkx as nx
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

# Create your views here.
from django.template.response import TemplateResponse

# from research.templatetags.research_extras import all_snippets
from research.data.misc_utils import get_advanced_query, get_date_parameter, format_for_gallery, get_web_html, \
    get_multimedia_html

from research.data.sesson_keys import SESSION_FULL_TEXT_SEARCH, SESSION_VALUE_CHANGED, SESSION_ENGINE_SEARCH, \
    SESSION_SDATE_SEARCH, SESSION_EDATE_SEARCH, SESSION_BOOL_AND_SEARCH, SESSION_BOOL_NOT_SEARCH, \
    SESSION_BOOL_OR_SEARCH, SESSION_LOC_SEARCH, SESSION_IS_CHANGED_KEY, SESSION_VALUE_NOT_CHANGED

# from discovery.research.data.misc_utils import get_web_html, get_multimedia_html
from model.myutils.clustering_utils import map_cluster_to_data, summarize_clusters
from model.myutils.data_utils import get_sentences, map_cluster_to_data_expanded, map_cluster_to_doc_expanded
from model.myutils.graph_builder import build_doc_graph, connect_mm_doc_to_clusters, expand_view
from model.myutils.my_files_utils import save_json, read_json

from model.research.clusters import get_agg_clust_assignment
from model.research.embeddings import get_sentence_embedding, search_through_embeddings
from model.research.results_aggregate import get_all_vertical_results

from django.http import HttpResponse
from django.views.decorators.clickjacking import xframe_options_exempt


@xframe_options_exempt
def index(request):
    if request.session.get('uid', None) is None:
        request.session['uid'] = str(uuid.uuid4())

    full_text_search = ""
    lookup_level = ""
    date_start = ""
    date_end = ""
    search_engine = ""
    boolean_and = ""
    boolean_or = ""
    boolean_not = ""
    location = ""

    parameters = dict()

    request.session[SESSION_IS_CHANGED_KEY] = SESSION_VALUE_NOT_CHANGED

    if 'ft_search' in request.GET:
        full_text_search = request.GET['ft_search']

        if request.session.get(SESSION_FULL_TEXT_SEARCH, SESSION_VALUE_CHANGED) != full_text_search:
            request.session[SESSION_FULL_TEXT_SEARCH] = full_text_search
            request.session[SESSION_IS_CHANGED_KEY] = SESSION_VALUE_CHANGED

    if 'lookup' in request.GET:
        lookup_level = request.GET['lookup']

    if 'engine' in request.GET:
        search_engine = request.GET['engine'].lower()
        parameters['engine'] = search_engine

        if request.session.get(SESSION_ENGINE_SEARCH, SESSION_VALUE_CHANGED) != search_engine:
            request.session[SESSION_ENGINE_SEARCH] = search_engine
            request.session[SESSION_IS_CHANGED_KEY] = SESSION_VALUE_CHANGED
    else:
        search_engine = 'google'
        parameters['engine'] = search_engine

    # if search_engine is None or search_engine == '':
    #     search_engine = 'qwant'

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

    # if False:
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

        print("test")
        search_results = get_all_vertical_results(query=query, num=100,
                                                  engine=search_engine)  # Initiate search results in real time
        search_results_sentences = get_sentences(
            search_results)  # Combine all the vailable text for embeddings with preprocessing
        search_result_sentence_embeddings = get_sentence_embedding(
            search_results_sentences)  # Get search results embeddings

        snip_view_process = search_through_embeddings(query, search_result_sentence_embeddings,
                                          search_results)  # save the snip view ordered by cosine relevancy

        # perform agg clustering
        search_results_cluster_assignment = get_agg_clust_assignment(search_result_sentence_embeddings,
                                                                     13.48)  # [1, 2,23...]
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
        mm_doc_clusters = get_agg_clust_assignment(mm_doc_sentences_embeddings, 15.52)
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
        # snip_view_process.join()

    clust_view = read_json('clust_view')
    doc_view = read_json('doc_view')
    snip_view = read_json('snip_view')

    wikilook = ""
    # Change view depending on the granularity selected
    if lookup_level == 'doc' or True:
        return render(request, 'content_doc.html',
                      {'clusters': clust_view, 'documents': doc_view, 'snippets': snip_view})
    elif lookup_level == 'snip':
        snip_view = format_for_gallery(snip_view)
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
        return render(request, 'content.html', {'clusters': clust_view, 'documents': doc_view, 'snippets': snip_view})


def get_document_preview(request):
    # TODO Update the doc review panel to take into consideration of the UUID
    doc_id = request.GET['doc_id']
    doc_view = read_json('doc_view')
    snip_view = read_json('snip_view')
    snip_list = doc_view[doc_id]['snips_list']

    snippets = []
    for snip_id in snip_list:
        snippets.append(snip_view[snip_id])

    return TemplateResponse(request, 'doct_preview.html',
                            {'doc_id': doc_id, 'documents': doc_view, 'snippets': snip_view, 'snip_list': snippets})
    # return HttpResponse(all_snippets(snip_view, snip_list, 0))


def homepage(request):
    return render(request, 'start_page.html', {})


@xframe_options_exempt
def viz(request):
    return render(request, 'viz.html', {})


def get_cluster_data(request):
    G = ""
    with open("/media/abdur/CE14CF6614CF4FDF/untitled/discovery/newdatatrimmedfixedNEW.json") as f:
        # with open("D:\\Backup\\PycharmProjects\\F1\\untitled\\research\\newdatatrimmedfixedNEW.json") as f:
        js_graph = json.load(f)
        G = nx.json_graph.node_link_graph(js_graph)

    node_id = request.GET['id']

    print(node_id)

    tree_struct = {}
    tree_struct.update({"id": node_id})
    tree_struct.update({"children": []})

    node = G.nodes(data=True)[node_id]
    tree_struct.update({"data": {"band": node['text'], "relation": "NA"}})
    tree_struct.update({"name": node['text']})

    clust_neigh = list(nx.neighbors(G, node_id))
    clust_children = []

    doc_dict = {}
    i = 0
    for neighbor in clust_neigh:
        doc_data = {}
        doc_show_data = ""

        if neighbor.endswith('c'):  # further expand
            # if i == 3:
            #     break
            # i += 1
            doc_text = G.nodes(data=True)[neighbor]['text']
            # doc_text = (doc_text[:20] + '..') if len(doc_text) > 20 else doc_text

            doc_data.update({"id": neighbor})
            doc_data.update({"name": doc_text})
            doc_data.update({"data": {"band": doc_text, "$color": "#f55"}})
            doc_data.update({"children": []})

            clust_children.append(doc_data)
        elif neighbor.endswith('d'):
            doc_text = G.nodes(data=True)[neighbor]['text']
            # doc_text = (doc_text[:20] + '..') if len(doc_text) > 20 else doc_text

            doc_data.update({"id": neighbor})
            doc_data.update({"name": doc_text})  # add doc meta
            doc_data.update({"data": {"band": doc_text, "relation": "NA"}})  # add cluster summary
            doc_data.update({"children": []})

            doc_neigh = list(nx.neighbors(G, neighbor))

            for snip in doc_neigh:
                snip_dict = {}
                if not snip.endswith('c'):
                    snip_dict.update({"id": snip})
                    if not snip.endswith('d'):  # its a snip
                        snip_dict.update({"name": G.nodes(data=True)[snip]['title']})

                        html_data = ""
                        type = G.nodes(data=True)[snip]['type']
                        if type == 'web':
                            html_data = get_web_html(G.nodes(data=True)[snip]['title'],
                                                     G.nodes(data=True)[snip]['snippet'],
                                                     G.nodes(data=True)[snip]['url'])

                            snip_dict.update({"data": {"band": html_data, "relation": "Part-of"}})
                        else:
                            html_data = get_multimedia_html(G.nodes(data=True)[snip]['title'],
                                                            G.nodes(data=True)[snip]['thumbnail'],
                                                            G.nodes(data=True)[snip]['url'])
                            snip_dict.update({"data": {"band": html_data, "relation": "Part-of"}})
                        doc_show_data += html_data
                    else:
                        summ = G.nodes(data=True)[neighbor]['text']
                        # summ = (doc_text[:20] + '..') if len(summ) > 20 else summ
                        snip_dict.update({"name": summ})
                        d_neigh = list(nx.neighbors(G, neighbor))

                        d_show_data = ""
                        for dn in d_neigh:
                            if dn.isnumeric():
                                html_data = ""
                                type = G.nodes(data=True)[dn]['type']
                                if type == 'web':
                                    html_data = get_web_html(G.nodes(data=True)[dn]['title'],
                                                             G.nodes(data=True)[dn]['snippet'],
                                                             G.nodes(data=True)[dn]['url'])
                                    # snip_dict.update({"data": {"band": html_data, "relation": "Part-of"}})
                                else:
                                    html_data = get_multimedia_html(G.nodes(data=True)[dn]['title'],
                                                                    G.nodes(data=True)[dn]['thumbnail'],
                                                                    G.nodes(data=True)[dn]['url'])
                                    # snip_dict.update({"data": {"band": html_data, "relation": "Part-of"}})
                                d_show_data += html_data
                        snip_dict.update({"data": {"band": d_show_data, "relation": "NA"}})

                    doc_data['children'].append(snip_dict)
                    doc_data.update({"data": {"band": doc_show_data, "relation": "NA"}})
            clust_children.append(doc_data)

    tree_struct["children"] = clust_children
    # print(tree_struct)

    return JsonResponse({'success': True, 'data': tree_struct})


def get_clusters(request):
    G = ""
    with open("/media/abdur/CE14CF6614CF4FDF/untitled/discovery/newdatatrimmedfixedNEW.json") as f:
        # with open("D:\\Backup\\PycharmProjects\\F1\\untitled\\research\\newdatatrimmedfixedNEW.json") as f:
        js_graph = json.load(f)
        G = nx.json_graph.node_link_graph(js_graph)

    full_text_search = 'Entered Query Visualization'
    if 'ft_search' in request.GET:
        full_text_search = request.GET['ft_search']

    tree_struct = {}
    tree_struct.update({"id": 'q'})
    tree_struct.update({"name": full_text_search})
    tree_struct.update({"children": []})
    tree_struct.update({"data": {"band": "NA", "relation": "NA"}})

    limit = 0
    for node in G.nodes(data=True):
        if not node[0].endswith('c'):
            continue

        query_clust = {}
        query_clust.update({"id": node[0]})
        query_clust.update({"name": node[1]['text']})
        query_clust.update({"children": []})

        clust_neigh = list(nx.neighbors(G, node[0]))
        clust_children = []

        doc_dict = {}
        nei_limit = 0

        for neighbor in clust_neigh:
            # break;
            doc_data = {}
            if neighbor.endswith('c'):  # further expand
                doc_text = G.nodes(data=True)[neighbor]['text']
                # doc_text = (doc_text[:20] + '..') if len(doc_text) > 20 else doc_text

                doc_data.update({"id": neighbor})
                doc_data.update({"name": doc_text})
                doc_data.update({"data": {"band": doc_text, "$color": "#f55"}})
                doc_data.update({"children": []})

                clust_children.append(doc_data)

                nei_limit += 1

                # if (nei_limit >= 4 ):
                # break;
        query_clust.update({"children": clust_children})
        tree_struct["children"].append(query_clust)

        limit += 1

        # if limit == 4:
        #     break

    return JsonResponse({'success': True, 'data': tree_struct})
# TODO Hide explore more cluster when it is empty
# Case 1: When it is all empty including no further multimedia documents to explore
# Case2: When only explore more cluster is empty yet there are multimedia documents further to explore
# TODO: Decrease the markjs highlight opacity
# FIXED: delay the exectuion of the date and engine button if the query is newly typed.
# FIXED: Error when organic results not found on the following req [30/Sep/2020 11:55:08] "GET /?lookup=clust&ft_search=Pakistan&notInput=coronavirus&sdate=08/01/2020&edate=08/31/2020 HTTP/1.1" 500 90430
# TODO: Lookup parameter in the URL is coming as a NULL
