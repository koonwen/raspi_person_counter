import sqlite3
from time import sleep


class Data(object):
    """Class for handling data sending/preprocessing"""

    def __init__(self, collection_limit=5):
        self.conn = sqlite3.connect('data.db')
        self.cur = self.conn.cursor()
        self.collection_limit = collection_limit
        self.current_collection_count = 0
        self.data = [0, 0, 0, 0, 0]
        self.detection_list = []
        self.post_data_semaphore = True

    def close_table(self):
        self.conn.commit()
        self.cur.close()

    def create_table(self):
        self.cur.execute(
            'CREATE TABLE Data('
            'img1 INTEGER,'
            'img2 INTEGER,'
            'img3 INTEGER,'
            'img4 INTEGER,'
            'img5 INTEGER,'
            'timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)'
        )

    def save_data(self):
        """Save data to file"""
        self.cur.execute('INSERT INTO Data(img1, img2, img3, img4, img5) VALUES(?, ?, ?, ?, ?)',
                         (self.data[0], self.data[1], self.data[2], self.data[3], self.data[4]))
        self.conn.commit()

    def process_result(self):
        """Processing routine called everytime image data comes in"""
        if self.current_collection_count < 5:
            self.current_collection_count += 1
            self.data[self.current_collection_count] = len(self.detection_list)
            print(self.data)
        else:
            self.current_collection_count = 0
            print(self.data)
            self.save_data()

    def timer_thread(self, time_interval):
        """Signal post event to run.py"""
        while self.post_data_semaphore:
            self.process_result()
            sleep(time_interval)
