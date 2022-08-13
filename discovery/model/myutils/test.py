# from datetime import datetime
#
# import dateutil
# from dateutil import tz
#
#
# def convert_date(date_time):
#     # METHOD 2: Auto-detect zones:
#     d = dateutil.parser.parse(date_time)
#     print(d.strftime('%d-%b-%Y'))  # ==> '24-Sep-2019'
# import requests
# import time
# import datetime
#
# resp = requests.get('https://swisscows.ch/generateApiGuardToken')
# api_token = resp.json()['token']
# time_stamp = time.mktime(datetime.datetime.now().timetuple()) * 1000
# headers = {'X-Requested-With': 'XMLHttpRequest', 'Cookie': 'hash={}'.format(resp.cookies['hash'])}
# resp = requests.get('https://swisscows.ch/?query=dogdog+hundefutter&region=de-CH&uiLanguage=browser&_={}&apiGuard={}'.format(time_stamp, api_token), headers=headers)
# print(resp.status_code)
# print(resp.json())

# importing the multiprocessing module
import multiprocessing


def print_cube(num):
    """
    function to print cube of given num
    """
    print("Cube: {}".format(num * num * num))


def print_square(num):
    """
    function to print square of given num
    """
    print("Square: {}".format(num * num))


# if __name__ == "__main__":
#     # creating processes
#     p1 = multiprocessing.Process(target=print_square, args=(10,))
#     p2 = multiprocessing.Process(target=print_cube, args=(10,))
#
#     # starting process 1
#     p1.start()
#     # wait until process 1 is finished
#     p1.join()
#     # starting process 2
#     p2.start()
#
#     # wait until process 1 is finished
#     p1.join()
#     # wait until process 2 is finished
#     p2.join()
#
#     # both processes finished
#     print("Done!")
# import requests
#
from myutils.my_files_utils import read_json
#
# options = {
#         'url': 'https://api.qwant.com/api/search/web?count=10&offset=0&q=Pakistan&t=web&locale=en_US&uiv=1',
#         'apikey': '5efc986944041403686fcdbcecf7a975b881'
#     }
#
# x = requests.post('https://api.wintr.com/fetch', data = options)
#
# y = x.json()
#
# import json
# z = json.loads(y['content'])
#
# save_json('qwaunt', z)
# print(x)

# z1 = read_json('qwaunt')
# z2 = read_json('qwaunt')
# z3 = read_json('qwaunt')
#
# test = z1['data']['result']['items']\
#     .extend(z2['data']['result']['items'])
#
# print(test)

# import datetime
#
# epoch = 1593686628
# ts = datetime.datetime.fromtimestamp(epoch).strftime('%d-%b-%Y')
# print(ts)