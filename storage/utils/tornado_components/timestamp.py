import time
import datetime

def get_time_stamp(self):
        ts = time.time()
        return datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d%H%M')