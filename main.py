import requests
import time
import json
import sys
import statistics
from datetime import datetime
import typer as typer
from typing import Optional
import pyperclip
import uncurl

DEFAULT_FILE = 'Reads value in clipboard'
DEFAULT_REPEATS = 10
DEFAULT_THREADS = 1
DEFAULT_REFRESHTIME = 5


def run_benchmarks(repeats, threads, refreshtime, context):
    url = context.url
    cookies = context.cookies
    headers = context.headers
    data = context.data
    payload = json.loads(data)

    for i in range(repeats):
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

        print('Response status code:', response.status_code)
        print('Response time:', delta_time, 'seconds')

        time.sleep(refreshtime)

def main(
        file: Optional[typer.FileText] = typer.Option(None, "--file", "-f", help='Path to file containing a cURL command to run.'),
        repeats: int = typer.Option(DEFAULT_REPEATS, "--repeats", "-r", help='Number of times to repeat cURL command.'),
        threads: int = typer.Option(DEFAULT_THREADS, "--threads", "-t", help='Number of threads to run cURL commands in parallel.'),
        refreshtime: int = typer.Option(DEFAULT_REFRESHTIME, "--refreshtime", help='Number of seconds between cURL commands.'),
        appname: str = typer.Option(None, "--name", help='Name of application.'),
        comment: str = typer.Option(None, "--comment", help='Optional comments.'),

):

    if file:
        # If provided with file, read the contents of the file
        curl = file.read()
    else:
        # Else get clipboard value
        curl = pyperclip.paste()

    context = uncurl.parse_context(curl)

    url = context.url
    cookies = context.cookies
    headers = context.headers
    data = context.data
    payload = json.loads(data)

    print("=" * 40)
    print(f"{'HttPyBench configuration':^40}")
    print("=" * 40)
    print(f"{'URL:':<15}{url}")
    print(f"{'Repeats:':<15}{repeats}")
    print(f"{'Threads:':<15}{threads}")
    print(f"{'App name:':<15}{appname}")
    print(f"{'Comments':<15}{comment}")
    print(f"{'Refresh time:':<15}{refreshtime}")
    print("=" * 40)


if __name__ == "__main__":
    typer.run(main)

#
# print('Starting benchmarks on ', appName, ' ...')
# print(comment)
#
#
# requestTimeList = []
#
#
#
# averageRequestTime = sum(requestTimeList) / len(requestTimeList)
# medianRequestTime = statistics.median(requestTimeList)
# dateTime = datetime.now()
#
# info = {
#     "appName": appName,
#     "comment": comment,
#     "dateTime": dateTime,
#     "requestTimeList": requestTimeList,
#     "averageRequestTime": averageRequestTime,
#     "medianRequestTime": medianRequestTime
# }
#
# filename = "results.json"
#
# try:
#     with open(filename, "r+") as f:
#         try:
#             existing_data = json.load(f)
#         except json.JSONDecodeError:
#             existing_data = []
#
#         existing_data.append(info)
#         f.seek(0)
#         json.dump(existing_data, f, indent=4, default=str)
#         f.truncate()
# except FileNotFoundError:
#     with open(filename, "w") as f:
#         existing_data = [info]
#         json.dump(existing_data, f, indent=4, default=str)
# finally:
#     f.close()
#
# print('Benchmarks finished!')
