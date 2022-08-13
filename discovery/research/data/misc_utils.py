import datetime


def get_list_if_val_exists(key, val):
    if val is not None:
        q = dict()
        q[key] = val
        return q
    else:
        return None


def get_advanced_query(and_term, or_term, not_term, full_term, engine='google'):
    query = full_term

    if and_term is not None:
        query = query + ' "' + and_term + '" '

    if engine == 'google':

        if or_term is not None:
            or_split = not_term.split()
            or_token = ' OR '.join(or_split)
    else:
        if or_term is not None:
            or_split = not_term.split()
            or_token = '|'.join(or_split)

    query = query + or_term

    if not_term is not None:
        not_split = not_term.split()
        not_token = ' -'.join(not_split)
        query = query + not_token

    return query

def get_date_parameter(date_start, date_end, engine='google'):
    return_date = ''
    if engine == '' or engine == 'google':
        # s = datetime.datetime.strptime(date_start, '%m/%d/%Y').strftime('%d/%m/%Y')
        # e = datetime.datetime.strptime(date_end, '%m/%d/%Y').strftime('%d/%m/%Y')

        return_date = 'cdr:1,cd_min:' + date_start + ',cd_max:' + date_end
        import urllib.parse
        return_date = urllib.parse.quote(return_date, safe="")

    else:
        s = datetime.datetime.strptime(date_start, '%m/%d/%Y').strftime('%Y-%m-%d')
        e = datetime.datetime.strptime(date_end, '%m/%d/%Y').strftime('%Y-%m-%d')

        return_date = s + '..' + e

    return return_date

def format_for_gallery(snip_view):
    group = dict()
    successive = False
    last_key = -1

    for key, item in snip_view.items():
        if item['type'] == 'image':
            if not successive:  # use a new key
                last_key = key
                print(key)

            if last_key in group:
                group[last_key]['gallery'].append({key: item})
            else:
                group[last_key] = {
                    'type': 'image',
                    'gallery': list()
                }

                group[last_key]['gallery'].append({key: item})

            successive = True
        else:
            group[key] = item

            successive = False
    return group

def get_web_html(title, snippet, url):
    html = '<a href="' + url + '" target="_blank">'+title+'</a> <br>'
    html += '<p style="font-size: 9px">'+snippet+'</p> <br> <hr>'

    return html

def get_multimedia_html(title, thumbnail, url):
    html = '<img src="' + thumbnail + '"  width="100%" /> <br>'
    html += '<a href="' + url + '" target="_blank">' + title + '</a> <br>  <hr>'

    return html
