import os
import requests
from requests.auth import HTTPBasicAuth
from time import sleep
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
ROUTE = os.environ["POST_DATA_ROUTE"]
USER = os.environ["USER"]
PASSWORD = os.environ["PASSWORD"]


class Data(object):
    """Class for handling data sending/preprocessing"""
    def __init__(self, collection_limit=5):
        self.collection_limit = collection_limit
        self.current_collection_count = 0
        self.data = dict()
        self.detection_list = []
        self.post_data_semaphore = True

    @property
    def mode_index(self):
        """return the mode index of the collection_limit"""
        return self.collection_limit//2

    def process_result(self):
        """Processing routine called everytime image data comes in"""
        if self.current_collection_count < 5:
            self.current_collection_count += 1
            self.data[f'img{self.current_collection_count}'] = len(self.detection_list)
            print(self.data)
        else:
            self.current_collection_count = 0
            self.data['mode'] = sorted([value for value in self.data.values()])[self.mode_index]
            self.data['timestamp'] = datetime.now().isoformat(sep=' ', timespec='seconds')
            print(self.data)
            self.post_data()

    def post_data(self):
        """Send data to the server"""
        try:
            r = requests.post(ROUTE, json=self.data, verify=True, timeout=2, auth=HTTPBasicAuth(USER, PASSWORD))
            r.raise_for_status()
            pass
        except Exception as err:
            print("Could not send data\n")
            print(err)
        finally:
            self.data.clear()
            sleep(1)

    def timer_thread(self, time_interval):
        """Signal post event to run.py"""
        while self.post_data_semaphore:
            self.process_result()
            sleep(time_interval)
