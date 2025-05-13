import time
import requests
from requests import Response
from datetime import datetime, timedelta

MAX_SIZE = 200
AMT_RETRIES = 10
RETRY_TIMER_MULT = 1.0 #amount of time increase per retry
CACHE_TIMEOUT = 300 #in seconds

key_order = []
key_times = {}
requests_cache = {}

def create_key(url: str, header: object, json: object, data_http: object) -> str:
    """
    Create key for cache lookups from request data
    """
    return f"{url};{str(header)};{str(json)};{str(data_http)}"

def do_retry_request(use_cache: bool, is_get: bool, url: str, header: object, json: object = None, data_http: object = None) -> Response:
    """
    Performs a HTTP request and retries some times if server error
    """
    #check in cache
    if use_cache:
        data = cache_lookup(url, header, json, data_http)
        if data:
            # print("cache " + create_key(url, header, json, data_http))
            return data
    # print("not cache " + create_key(url, header, json, data_http))
    #create request function
    if is_get:
        request_func = lambda: requests.get(url, headers=header)
    else:
        request_func = lambda: requests.post(url, data=data_http, json=json, headers=header)
    #do request
    data = request_func()
    atts = 0
    while (data.status_code - 1) // 100 == 5 and atts < AMT_RETRIES: #the -1 is to ignore code 500 (genious)
        throttle_time = data.json()["ThrottleSeconds"]
        if throttle_time != 0:
            time.sleep(throttle_time)
        else:
            time.sleep(1 + atts * RETRY_TIMER_MULT)
        data = request_func()
        atts += 1
        #print(f"Attempt {atts} Code {data.status_code}")
    #add to cache
    if use_cache and data:
        insert_cache(data, url, header, json, data_http)
    return data

def insert_cache(data: object, url: str, header: object, json: object, data_http: object) -> None:
    """
    Inserts into cache
    """
    key = create_key(url, header, json, data_http)
    #add data to cache and refresh timer
    requests_cache[key] = data
    key_times[key] = datetime.now()
    #refresh LRU order and maintain cache size
    if key not in key_order:
        key_order.insert(0, key)
        while len(key_order) > MAX_SIZE:
            last_key = key_order.pop()
            key_times.pop(last_key)
            requests_cache.pop(last_key)
    else:
        key_order.remove(key)
        key_order.insert(0, key)

def cache_lookup(url: str, header: object, json: object, data_http: object) -> object:
    """
    Looks if request is in cache, returns data if it is
    """
    key = create_key(url, header, json, data_http)
    if key in requests_cache:
        #check if cache is outdated
        if (datetime.now() - key_times[key]).total_seconds() > CACHE_TIMEOUT:
            key_order.remove(key)
            key_times.pop(key)
            requests_cache.pop(key)
            return None
        #refresh LRU
        key_order.remove(key)
        key_order.insert(0, key)
        return requests_cache[key]
    return None
