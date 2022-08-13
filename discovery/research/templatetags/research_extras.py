from urllib.parse import urlparse

from django import template
from django.utils.safestring import mark_safe
from django.utils.text import Truncator

register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def get_summary(dictionary, key):
    data = dictionary.get(key)['summary']
    return data #(data[:40] + '...') if len(data) > 40 else data
    # return dictionary.get(key)['summary']


@register.filter
def get_clust_docs(dictionary, key):
    return dictionary.get(key)['docs_list']


@register.filter
def get_snippets(dictionary, key):  # it will return a list of snippets from docs dict
    return dictionary.get(key)['snips_list']


@register.filter
def get_images(snip_dict, list_snip_id):
    images = []
    for snippet in list_snip_id:
        if snip_dict.get(snippet).type == 'image':
            images.append(snippet)

    return images


@register.filter
def get_domain(args, url):
    return urlparse(url).netloc


@register.filter
def get_count(dictionary):
    length = len(dictionary)
    if length > 0:
        return '({})'.format(length)
    else:
        return ''


@register.simple_tag
def gallery(snip_dict, snip_list, doc_id, doc_dict=None):
    images = []
    result = ""
    counter = 0
    dict_of_images = {}

    if type(doc_id) == list:  # its a list of docs
        # for each doc
        for doc in doc_id:
            dict_of_images[doc] = list()

            snips = doc_dict[doc]['snips_list']
            # get images image
            for snip in snips:
                try:
                    if snip_dict[snip]['type'] == 'image' or snip_dict[snip]['type'] == 'video':
                        if snip_dict[snip]['thumbnail'].strip():  # If not empty thumbnail
                            dict_of_images[doc].append(
                                '<img src = "' + snip_dict[snip]['thumbnail'] + '" style="width:100%">')
                except KeyError:
                    print('NA')
        doc_counter = 0

        while len(images) < 4 and doc_counter < len(dict_of_images):
            images.extend(return_optimimal_snips(dict_of_images, doc_counter))
            doc_counter = doc_counter + 1

        if len(images) > 3:
            images = images[0:3]

        for image in images:
            result = result + '<div>' + image.replace('style="width:100%"',
                                                      'style="width:90%; height:60px; margin-top: 5px; margin-left: 15px"') + '</div>'

        return mark_safe(result)
    else:
        for item in snip_list:
            if counter == 4:
                break
            # TODO: To decide whether the news images should display in gallery or not since they are part of web links
            if snip_dict.get(item, dict()).get('type', '') == "image" or snip_dict.get(item, dict()).get(
                'type', '') == "video":  # or snip_dict[item]['type'] == "news":
                if snip_dict[item]['thumbnail'].strip():  # If not empty thumbnail
                    counter = counter + 1
                    images.append('<img src = "' + snip_dict[item]['thumbnail'] + '" style="width:100%">')

    if len(images) > 4:
        images = images[0:4]

    if len(images) == 4:
        result = result + '<div class="column">' + images[0] + images[1] + '</div>'
        result = result + '<div class="column">' + images[2] + images[3] + '</div>'
    elif len(images) == 3:
        result = result + '<div class="column">' + images[0] + images[1] + '</div>'
        result = result + '<div class="column">' + images[2].replace('style="width:100%"',
                                                                     'style="width:100%; height:120px"') + '</div>'
    elif len(images) == 2:
        result = result + '<div class="column">' + images[0].replace('style="width:100%"',
                                                                     'style="height:120px"') + '</div>'
        result = result + '<div class="column">' + images[1].replace('style="width:100%"',
                                                                     'style="height:120px"') + '</div>'
    elif len(images) == 1:
        result = result + '<div>' + images[0].replace('style="width:100%"',
                                                      'style="height:120px"') + '</div>'

    return mark_safe(result)

# TODO: should you include the video or images snippets in the Doc preview in case if web or news snippets stand low
@register.simple_tag
def links(snip_dict, snip_list, doc_id, doc_dict=None):
    result = ""
    counter = 0
    dict_of_links = {}
    links = list()

    if type(doc_id) == list:  # its a list of docs
        # for each doc
        for doc in doc_id:
            dict_of_links[doc] = list()

            snips = doc_dict[doc]['snips_list']
            # get first web/news
            for snip in snips:
                try:
                    if snip_dict[snip]['type'] == 'news' or snip_dict[snip]['type'] == 'web':
                        dict_of_links[doc].append('<div><a href = "' + snip_dict[snip][
                            'url'] + '" class ="snip-news" >' + Truncator(
                            snip_dict[snip]['title']).chars(45) + '</a></div>')
                except KeyError:
                    print("NF")

        link_counter = 0
        while len(links) < 3 and link_counter < len(dict_of_links):
            links.extend(return_optimimal_snips(dict_of_links, link_counter))
            link_counter = link_counter + 1

        if len(links) > 3:
            return mark_safe(' '.join(links[0:3]))
        else:
            return mark_safe(' '.join(links[0:3]))
    else:
        for item in snip_list:
            if counter == 3:
                break

            try:
                if snip_dict[item]['type'] == "news" or snip_dict[item]['type'] == "web":
                    result = result + '<div><a href = "' + snip_dict[item][
                        'url'] + '" class ="snip-news auto-hyphen" >' + Truncator(
                        snip_dict[item]['title']).chars(45) + '</a></div>'
                    counter = counter + 1
            except KeyError:
                print("NF")

    return mark_safe(result)

    # @register.simple_tag
    # def all_snippets(snip_dict, snip_list, doc_id):
    #     all_snips = []
    #
    #     for idx, item in enumerate(snip_list):
    #         if snip_dict[item]['type'] == "image":
    #             all_snips.append(image(snip_dict[item]))
    #         elif snip_dict[item]['type'] == "web":
    #             all_snips.append(web(snip_dict[item]))
    #         elif snip_dict[item]['type'] == "news":
    #             all_snips.append(news(snip_dict[item]))

    # print(*all_snips)
    return mark_safe(''.join(all_snips))


@register.simple_tag
def documents_title(doc_dict, doc_ids):
    # print(doc_ids)
    doc_summary = list()
    for i, doc_id in enumerate(doc_ids):
        if i == 3:
            break
        doc_summary.append('<div class="row doc-title-overview doc-title-click" id="' + doc_id + '">' + doc_dict[doc_id]['summary'][
                                                                                        0:50] + '...</div>')

    return mark_safe("".join(doc_summary))


# def web(snippet):
#     return '<div class="web"> <a href="' + snippet['url'] + '">' + snippet['title'] + ' - <span class="domain">' + urlparse(snippet['url']).netloc + '</span></a> <p class="text-muted">' + snippet['snippet'] + '</p> </div>'
#
# def image(snippet):
#     return '<div class="image"><a href="' + snippet['url'] + '"> <img src="' + snippet['thumbnail'] + '" alt="' + snippet['title'] + '" height="100%" width="100%"></a><span class="bold">Image: </span><h7 class="text-center font-italic text-muted">' + snippet['title'] + '</h7></div>'
#
# def vidnew(snippet):
#     return '<div class="news video"><div class="row"><div class="col-md-4"><img src="' + snippet['thumbnail'] + '" alt="' + snippet['title'] + '" height="90%" width="100%"></div><div class="col-md-8"><a href="' + snippet['url'] + '">' + snippet['title'] + '</a> <br><a href="' + snippet['url'] + '" class="text-info">' + snippet['url'] + '</a><p class="text-muted">This</p></div></div></div>'
#
# def news(snippet):
#     return '<div class="news"><div class="row"><img src="' + snippet['thumbnail'] + '" alt="' + snippet['title'] + '" height="40px" width="50px"><div class="col-md-12"><a href="' + snippet['url'] + '">' + snippet['title'] + '</a> <br><a href="' + snippet['url'] + '" class="text-info">' + snippet['snippet'] + '</a><p class="text-muted">This</p></div></div></div>'

def return_optimimal_snips(dict_of_images, fetch_loc):
    images = []
    counter = 0

    for item, value in dict_of_images.items():
        if counter == 3:
            break

        if len(value) > fetch_loc:
            images.append(value[fetch_loc])
            counter = counter + 1

    return images
