import requests
from requests.auth import HTTPBasicAuth
import dotenv
import os
from datetime import datetime

dotenv.load_dotenv()

ROUTE = os.environ["POST_DATA_ROUTE"]
USER = os.environ["USER"]
PASSWORD = os.environ["PASSWORD"]

test_data = {'img1': 0, 'img2': 0, 'img3': 0, 'img4': 0, 'img5': 0, 'mode': 0, 'timestamp': datetime.now().isoformat()}

def post_data_test():
    try:
        r = requests.post(ROUTE, json=test_data, verify=True, timeout=2,
                              auth=HTTPBasicAuth('pi', 'test'))
        r.raise_for_status()
    except Exception as err:
        print("Could not send data\n")
        print(err)

if __name__ == "__main__":
	post_data_test()
