# import json
#
#
# def read_json(file_name):
#
#     file_name = file_name
#     with open(file_name, 'r') as openfile:
#         # Reading from json file
#         return json.load(openfile)
#
# #
# # snip_view = read_json('snip_view')
# # group = dict()
# # successive = False
# # last_key = -1
# #
# # for key, item in snip_view.items():
# #     if key == '16':
# #         print('break')
# #     if item['type'] == 'image':
# #         if not successive:  # use a new key
# #             last_key = key
# #             print(key)
# #
# #         if last_key in group:
# #             group[last_key]['items'].append({key: item})
# #         else:
# #             group[last_key] = {
# #                 'type': 'image',
# #                 'items': list()
# #             }
# #
# #             group[last_key]['items'].append({key: item})
# #
# #         successive = True
# #     else:
# #         group[key] = item
# #
# #         successive = False
#
#
# # print(format(snip_view))
# # for key, item in images_dict.items():