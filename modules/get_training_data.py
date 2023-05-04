"""
Getting input data for model
"""
import os
from io import BytesIO
import pandas as pd
import pickle
from zipfile import ZipFile
from urllib.request import urlopen
import time


def get_data(progress_queue):

    progress_queue.put((10, "Getting training data"))
    time.sleep(1)
    # Download Cisco Umbrella Popularity List (legit).
    if not os.path.isfile('input data/top-1m.csv'):
        resp = urlopen('http://s3-us-west-1.amazonaws.com/umbrella-static/top-1m.csv.zip')
        zipfile = ZipFile(BytesIO(resp.read()))
        zipfile.extractall("input data")
    progress_queue.put((25, "Download Finished"))

    format_data(progress_queue)


def format_data(progress_queue):

    training_data = {'legit': [], 'dga': []}

    progress_queue.put((30, "Reduction to a unified form"))
    time.sleep(1)
    # print("[*] Reduction to a unified form...")
    # Extract second-level domain.
    for _ in training_data.items():
        domain_list = pd.read_csv('input data/top-1m.csv', names=['domain'])
        domain_list['domain'] = domain_list.applymap(lambda x: x.split('.')[0].strip().lower())
        domain_list['type'] = 'legit'
        training_data['legit'] = domain_list

        domain_list = pd.read_csv('input data/dga.csv', names=['domain'])
        domain_list['domain'] = domain_list.applymap(lambda x: x.split('.')[0].strip().lower())
        domain_list['type'] = 'dga'
        training_data['dga'] = domain_list

    progress_queue.put((70, "Saving training data to disk"))
    time.sleep(1)
    # print("[*] Saving training data to disk...")
    with open('input data/training_data.pkl', 'wb') as f:
        pickle.dump(training_data, f, pickle.HIGHEST_PROTOCOL)
    progress_queue.put((100, "Finished"))
    time.sleep(1)


if __name__ == "__main__":
    get_data()
    format_data()
