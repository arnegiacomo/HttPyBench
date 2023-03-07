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
import threading

DEFAULT_REPEATS = 10
DEFAULT_THREADS = 1
DEFAULT_REFRESHTIME = 5


def run_benchmarks(context, repeats, refreshtime):
    url = context.url
    cookies = context.cookies
    headers = context.headers
    data = context.data
    payload = json.loads(data)

    response_times = []

    for i in range(repeats):
        start_time = time.time()

        response = requests.post(
            url,
            cookies=cookies,
            headers=headers,
            json=payload,
        )

        end_time = time.time()
        delta_time = end_time - start_time

        response_times.append(delta_time)
        print(f"[{threading.current_thread().name}] Sent request to {url}")
        print(f"[{threading.current_thread().name}] Response status code: {response.status_code}")
        print(f"[{threading.current_thread().name}] Response time: {delta_time:.2f} seconds")

        time.sleep(refreshtime)

    average_response_time = sum(response_times) / len(response_times)
    median_response_time = statistics.median(response_times)
    timestamp = datetime.now()


def start_threads(context, repeats, refreshtime, number_of_threads):
    threads = []

    for i in range(number_of_threads):
        thread = threading.Thread(target=run_benchmarks, args=(context, repeats, refreshtime), name=str(i))
        thread.start()
        threads.append(thread)


def main(
        file: Optional[typer.FileText] = typer.Argument(None, help='Path to file containing a cURL command to run. Will use clipboard value if not provided. \033[1mMust only contain a single valid cURL command!\033[0m'),
        repeats: int = typer.Option(DEFAULT_REPEATS, "--repeats", "-r", help='Number of times to repeat cURL command.'),
        threads: int = typer.Option(DEFAULT_THREADS, "--threads", "-t", help='Number of threads to run cURL commands in parallel.'),
        refreshtime: int = typer.Option(DEFAULT_REFRESHTIME, "--refreshtime", help='Number of seconds between cURL commands.'),
        appname: str = typer.Option(None, "--name", "-n", help='Name of application.'),
        comment: str = typer.Option(None, "--comment", "-c", help='Optional comments.'),
):

    if file is not None:
        # If provided with file, read the contents of the file
        curl = file.read()
    else:
        # Else get clipboard value
        curl = pyperclip.paste()

    context = uncurl.parse_context(curl)

    print("=" * 40)
    print(f"{'HttPyBench':^40}")
    print("=" * 40)
    print(f"{'URL:':<15}{context.url}")
    print(f"{'Repeats:':<15}{repeats}")
    print(f"{'Threads:':<15}{threads}")
    print(f"{'App name:':<15}{appname}")
    print(f"{'Comments':<15}{comment}")
    print(f"{'Refresh time:':<15}{refreshtime}")
    print("=" * 40)

    start_threads(context, repeats, refreshtime, threads)


if __name__ == "__main__":
    typer.run(main)

#
# print('Starting benchmarks on ', appName, ' ...')
# print(comment)
#
#
#
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
