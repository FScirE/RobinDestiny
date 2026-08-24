import time
import requests
from requests import Response
from datetime import datetime

MAX_SIZE = 200
AMT_RETRIES = 10
RETRY_TIMER_MULT = 1.0 #amount of time increase per retry
CACHE_TIMEOUT = 300 #in seconds

key_order = []
key_times = {}
requests_cache = {}

manifest_key_order = []
manifest_cache = {}

def create_key(url: str, header: object, json: object, data_http: object) -> str:
    """
    Create key for cache lookups from request data
    """
    return f"{url};{str(header)};{str(json)};{str(data_http)}"

def do_retry_request(use_cache: bool, is_get: bool, url: str, header: object, json: object = None, data_http: object = None, manifest: bool = False) -> Response:
    """
    Performs a HTTP request and retries some times if server error
    """
    #check in cache
    if use_cache:
        data = cache_lookup(url, header, json, data_http, manifest)
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
        insert_cache(data, url, header, json, data_http, manifest)
    return data

def insert_cache(data: object, url: str, header: object, json: object, data_http: object, manifest: bool = False) -> None:
    """
    Inserts into cache
    """
    key = create_key(url, header, json, data_http)
    cache = manifest_cache if manifest else requests_cache
    order = manifest_key_order if manifest else key_order
    times = None if manifest else key_times
    #add data to cache and refresh timer
    cache[key] = data
    if times is not None:
        times[key] = datetime.now()
    #refresh LRU order and maintain cache size
    if key not in order:
        order.insert(0, key)
        while len(order) > MAX_SIZE:
            last_key = order.pop()
            if times is not None:
                times.pop(last_key)
            cache.pop(last_key)
    else:
        order.remove(key)
        order.insert(0, key)

def cache_lookup(url: str, header: object, json: object, data_http: object, manifest: bool = False) -> object:
    """
    Looks if request is in cache, returns data if it is
    """
    key = create_key(url, header, json, data_http)
    cache = manifest_cache if manifest else requests_cache
    order = manifest_key_order if manifest else key_order
    if key in cache:
        #check if cache is outdated
        if not manifest and (datetime.now() - key_times[key]).total_seconds() > CACHE_TIMEOUT:
            order.remove(key)
            key_times.pop(key)
            cache.pop(key)
            return None
        #refresh LRU
        order.remove(key)
        order.insert(0, key)
        return cache[key]
    return None
