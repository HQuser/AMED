import json
import multiprocessing
from functools import partial

import requests

def retrieve_all_verticals(query='mcdonalds', num=100, engine="google"):

    web_json = fetch_results_json(query=query, engine=engine, type='web', num=num)
    images_json = fetch_results_json(query=query, engine=engine, type='images', num=num)
    news_json = fetch_results_json(query=query, engine=engine, type='news', num=num)
    videos_json = fetch_results_json(query=query, engine=engine, type='videos', num=num)

    # Aggregate all into a datastructure
    dict = {
        'web': web_json,
        'images': images_json,
        'news': news_json,
        'videos': videos_json
    }

    return dict

'''
    This function is the main entry point for calling APIs with paramteres
'''


# TODO make UI to embed all the filters in the query before submittnig here
def fetch_results_json(query='mcdonalds', type='web', num=100, engine="google"):
    if engine == 'google':
        vertical_codes = {'images': ('tbm', 'isch'),
                          'news': ('tbm', 'nws'),
                          'videos': ('tbm', 'vid')}

        # from serpapi.google_search_results import GoogleSearchResults
        from serpapi import GoogleSearch as GoogleSearchResults

        params = {
            "engine": "google",
            "q": query,
            'num': 100,
            "api_key": "YOUR_KEY",
            "google_domain": "google.com",
            "hl": "en"
        }

        if type != 'web':  # if not web then specify vertical code
            params.update({vertical_codes[type][0]: vertical_codes[type][1]})  # take key as vertical : value as code

        client = GoogleSearchResults(params)
        results = client.get_dict()
        return results

    elif engine == 'bing':
        subscription_key = "YOUR_KEY"
        search_url = {
            'web': "https://api.cognitive.microsoft.com/bing/v7.0/search",
            'images': "https://api.cognitive.microsoft.com/bing/v7.0/images/search",
            'news': "https://api.cognitive.microsoft.com/bing/v7.0/news",
            'videos': "https://api.cognitive.microsoft.com/bing/v7.0/videos/search"
        }

        headers = {"Ocp-Apim-Subscription-Key": subscription_key}
        params = {"q": query, "textDecorations": True, "textFormat": "HTML", 'count': 100}

        response = requests.get(search_url[type], headers=headers, params=params)
        response.raise_for_status()
        search_results = response.json()

        return search_results
    elif engine == 'qwant':
        search_url = "https://api.qwant.com/api/search/" + type

        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0',
        }

        if type == 'web':
            # send 10 Simultaneously requests
            # if __name__ == '__main__':
            pool = multiprocessing.Pool(processes=(multiprocessing.cpu_count() - 1))
            iterable = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

            func = partial(fetch_100_web_fro_qwuant, query)
            result = pool.map(func, iterable)
            pool.close()
            pool.join()

            for num, res_json in enumerate(result, start=0):
                if num == 0:
                    continue

                result[0]['data']['result']['items'].extend(res_json['data']['result']['items'])
            # print(result)

            return result[0]
        else:
            params = {"count": 100, "offset": 0, "q": query, 't': type, 'locale': 'en_US', 'uiv': 1}

            response = requests.get(search_url, headers=headers, params=params)
            response.raise_for_status()
            search_results = response.json()

            return search_results


def fetch_100_web_fro_qwuant(query='mcdonalds', offset=0):
    type = 'web'
    print(offset)
    search_url = "http://api.scraperapi.com/?api_key=YOUR_KEY&url=https://api.qwant.com/api/search/" + type
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0', }
    params = {"count": 10, "offset": offset, "q": query, 't': type, 'locale': 'en_US', 'uiv': 1}

    options = {
        'url': 'https://api.qwant.com/api/search/web?count=10&offset=0&q=Pakistan&t=web&locale=en_US&uiv=1',
        'apikey': 'YOUR_KEY'
    }

    response = requests.post('https://api.wintr.com/fetch', data=options)

    search_results = response.json()
    # print(search_results)

    y = search_results['content']
    z = json.loads(y)
    return z

# cache_all_verticals()
# fetch_results_json(engine='test', type = 'news')
