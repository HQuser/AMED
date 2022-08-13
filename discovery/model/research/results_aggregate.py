# cache_all_verticals()
from model.myutils.my_preprocessor import get_words_from_url, normalize_encoded_chars, convert_date, convert_date_epoc
from model.research.api_calls import retrieve_all_verticals


def process_web(api_response, index=0, engine="google"):
    dict = {}
    offset = 0

    if engine == 'google':

        for number, result in enumerate(api_response['organic_results'], start=index):
            if 'title' not in result:
                offset = offset - 1
                continue

            if 'snippet' not in result:
                snip = ""
            else:
                snip = normalize_encoded_chars(result['snippet'])

            # print(f"{number + offset}. {result['title']} {result['snippet']}")
            dict[number + offset] = {'title': normalize_encoded_chars(result['title']),
                                     'snippet': snip,
                                     'url': result['link'],
                                     'type': 'web'}

    elif engine == 'bing':
        for number, result in enumerate(api_response['webPages']['value'], start=index):
            dict[number + offset] = {'title': normalize_encoded_chars(result['name']),
                                     'snippet': normalize_encoded_chars(result['snippet']),
                                     'url': result['url'],
                                     'type': 'web'}
            # print(convert_date(result['dateLastCrawled']))
    elif engine == 'qwant':
        for number, result in enumerate(api_response['data']['result']['items'], start=index):
            dict[number + offset] = {'title': normalize_encoded_chars(result['title']),
                                     'snippet': normalize_encoded_chars(result['desc']),
                                     'url': result['url'],
                                     'type': 'web'}
    return dict


def process_images(api_response, index=1, engine="google"):
    dict = {}

    if engine == 'google':
        offset = 0
        for number, result in enumerate(api_response['images_results'], start=index):
            # print(f"{number}. {result['title']} {result['link']}")
            if 'thumbnail' not in result or 'title' not in result:
                print(result)
                offset = offset - 1
                continue
            dict[number + offset] = {'title': normalize_encoded_chars(result['title']),
                            'url': result['link'],
                            'thumbnail': result['thumbnail'],
                            'type': 'image'}
    elif engine == 'bing':
        for number, result in enumerate(api_response['value'], start=index):
            dict[number] = {'title': normalize_encoded_chars(result['name']),
                            'url': result['hostPageUrl'],
                            'thumbnail': result['thumbnailUrl'],
                            'type': 'image'}

            # print(convert_date(result['datePublished']))
    elif engine == 'qwant':
        for number, result in enumerate(api_response['data']['result']['items'], start=index):
            dict[number] = {'title': normalize_encoded_chars(result['title']),
                            'url': result['url'],
                            'thumbnail': result['thumbnail'],
                            'type': 'image'}

    return dict


def process_news(api_response, index=1, engine="google"):
    dict = {}

    if engine == 'google':
        for number, result in enumerate(api_response['news_results'], start=index):
            # print(f"{number}. {result['title']} {result['snippet']}")
            if result['title'] == "":
                title = get_words_from_url(result['link'])
                print(f"{number}. {title}")
            else:
                title = result['title']
                title = normalize_encoded_chars(title)

            if 'thumbnail' not in result:
                thumbnail = ""
            else:
                thumbnail = result['thumbnail']
            dict[number] = {'title': title,
                            'snippet': result['snippet'],
                            'uploaded': result['date'],
                            'url': result['link'],
                            'thumbnail': thumbnail,
                            'type': 'news'}
    elif engine == 'bing':
        for number, result in enumerate(api_response['value'], start=index):
            dict[number] = {'title': result['name'],
                            'snippet': result['description'],
                            'uploaded': convert_date(result['datePublished']),
                            'url': result['url'],
                            'thumbnail': result['image']['thumbnail']['contentUrl'],
                            'type': 'news'}
    elif engine =='qwant':
        for number, result in enumerate(api_response['data']['result']['items'], start=index):
            try:
                thumb = result['media'][0]['pict']['url']
            except IndexError:
                thumb = ''

            dict[number] = {'title': result['title'],
                            'snippet': result['desc'],
                            'uploaded': convert_date_epoc(result['date']),
                            'url': result['url'],
                            'thumbnail': thumb,
                            'type': 'news'}

    return dict


def process_videos(api_response, index=1, engine="google"):
    dict = {}

    if engine == 'google':

        for number, result in enumerate(api_response['video_results'], start=index):
            if 'thumbnail' not in result:
                thumbnail = ""
            else:
                thumbnail = result['thumbnail']

            # if result['snippet'] is None:
            #     result['snippet'] = ""

            uploaded = ""
            if 'rich_snippet' in result:
                if 'top' in result['rich_snippet']:
                    if 'extensions' in result['rich_snippet']:
                        uploaded = " - ".join(result['rich_snippet']['top']['extensions'])
            else:
                print(result)

            dict[number] = {'title': normalize_encoded_chars(result['title']),
                            'snippet': '',
                            'uploaded': uploaded,
                            'thumbnail': thumbnail,
                            'url': result['link'],
                            'type': 'video'}
    elif engine == 'bing':
        for number, result in enumerate(api_response['value'], start=index):
            dict[number] = {'title': normalize_encoded_chars(result['name']),
                            'snippet': normalize_encoded_chars(result['description']),
                            'uploaded': convert_date(result['datePublished']) + ' - ' + result['creator']['name'],
                            'thumbnail': result['thumbnailUrl'],
                            'url': result['hostPageUrl'],
                            'type': 'video'}
    elif engine == 'qwant':
        for number, result in enumerate(api_response['data']['result']['items'], start=index):
            dict[number] = {'title': normalize_encoded_chars(result['title']),
                            'snippet': normalize_encoded_chars(result['desc']),
                            'uploaded': convert_date_epoc(result['date']) + ' - ' + result['channel'],
                            'thumbnail': result['thumbnail'],
                            'url': result['url'],
                            'type': 'video'}

    return dict


# Process retrived results into 1 semantic container
def get_all_vertical_results(query='mcdonalds', num=100, engine="google"):
    api = retrieve_all_verticals(query=query, num=num, engine=engine)
    web = process_web(api['web'], engine=engine)
    images = process_images(api['images'], len(web), engine=engine)
    news = process_news(api['news'], len(images) + len(web), engine=engine)
    videos = process_videos(api['videos'], len(news) + len(images) + len(web), engine=engine)

    dicts = {**web, **images, **news, **videos}
    return dicts

# get_all_vertical_results()
