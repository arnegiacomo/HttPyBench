import requests
import time
import json
import statistics
from datetime import datetime
import os
import argparse
import sys
import uncurl
context = uncurl.parse_context('''''')
url = context.url
cookies = context.cookies
headers = context.headers
data = context.data
json = json.loads(data)

print(type(json))
print(url, cookies, headers, json)


appName = ''
comment = ''

print('Starting benchmarks on ', appName, ' ...')
print(comment)

NumberOfRequests = 30
RefreshTimeSeconds = 5

requestTimeList = []

for i in range(NumberOfRequests):
    start_time = time.time()
    print('Sending HTTP request: ', url)

    response = requests.post(
        url,
        cookies=cookies,
        headers=headers,
        json=json,
    )

    end_time = time.time()
    delta_time = end_time - start_time
    requestTimeList.append(delta_time)
    print('Response status code:', response.status_code)
    print('Response time:', delta_time, 'seconds')

    time.sleep(RefreshTimeSeconds)

averageRequestTime = sum(requestTimeList) / len(requestTimeList)
medianRequestTime = statistics.median(requestTimeList)
dateTime = datetime.now()

info = {
    "appName": appName,
    "comment": comment,
    "dateTime": dateTime,
    "requestTimeList": requestTimeList,
    "averageRequestTime": averageRequestTime,
    "medianRequestTime": medianRequestTime
}

filename = "results.json"

try:
    with open(filename, "r+") as f:
        try:
            existing_data = json.load(f)
        except json.JSONDecodeError:
            existing_data = []

        existing_data.append(info)
        f.seek(0)
        json.dump(existing_data, f, indent=4, default=str)
        f.truncate()
except FileNotFoundError:
    with open(filename, "w") as f:
        existing_data = [info]
        json.dump(existing_data, f, indent=4, default=str)
finally:
    f.close()

print('Benchmarks finished!')
