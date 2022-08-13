import json
import os
from pathlib import Path

from django.http import request


def save_json(file_name, json_data):
    # SAVING JSON
    # my_path = os.path.abspath(os.path.dirname(__file__))
    path = Path(__file__).parent / (
                "../../discovery/research/data/" + file_name)
    # path = "C:\\Users\\abdur\\PycharmProjects\\untitled\\discovery\\research\\data\\" + file_name
    with open(path, "w") as outfile:
        json.dump(json_data, outfile)


def read_json(file_name):
    path = Path(__file__).parent / (
                "../../discovery/research/data/" + file_name)

    with open(path, 'r') as openfile:
        # Reading from json file
        return json.load(openfile)


def write_csv(dict_data, csv_columns, csv_file):
    import csv
    # csv_file = "report/" + csv_file
    with open(csv_file, mode='w', encoding='utf-8') as csv_file:
        fieldnames = csv_columns
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()
        for k, v in dict_data.items():
            writer.writerow(v)
            # writer.writerow({'emp_name': 'Erica Meyers', 'dept': 'IT', 'birth_month': 'March'})


def write_csv_kv(dict_data, csv_file):
    import csv
    with open('dict.csv', 'w', newline="", encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in dict_data.items():
            writer.writerow([key, value])
