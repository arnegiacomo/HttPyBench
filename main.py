import requests as r
import time
import json
import statistics
from datetime import datetime
import typer as typer
from typing import Optional
import pyperclip
import uncurl
import threading
import queue

DEFAULT_REQUESTS = 10
DEFAULT_THREADS = 1
DEFAULT_THREAD_CREATION_DELAY = 0
DEFAULT_REFRESHTIME = 5

result_queue = queue.Queue()
worker_threads = []


def benchmark_worker(context, requests, refreshtime):
    url = context.url
    method = context.method
    cookies = context.cookies
    headers = context.headers
    data = context.data
    payload = {}
    if data:
        payload = json.loads(data)

    response_times = []

    for i in range(requests):
        try:
            start_time = time.time()
            response = r.request(
                method,
                url,
                cookies=cookies,
                headers=headers,
                json=payload,
            )
            end_time = time.time()
            delta_time = end_time - start_time
            response_times.append(delta_time)

            print(f"[{threading.current_thread().name}] Sent {method} request to {url}")
            print(f"[{threading.current_thread().name}] Response status code: {response.status_code}")
            print(f"[{threading.current_thread().name}] Response time: {delta_time:.2f} seconds")

        except requests.exceptions.ConnectionError as e:
            print(f"[{threading.current_thread().name}] Connection refused when sending request to {url}")
            print(f"[{threading.current_thread().name}] Error: {e}")

        time.sleep(refreshtime)

    if len(response_times) != 0:
        average_response_time = sum(response_times) / len(response_times)
        median_response_time = statistics.median(response_times)
        timestamp = datetime.now()

        result_queue.put(average_response_time)
    else:
        print(f"[{threading.current_thread().name}] No successful {method} requests to {url}")


def start_threads(context, requests, refreshtime, number_of_threads, thread_creation_delay):

    for i in range(number_of_threads):
        thread = threading.Thread(target=benchmark_worker, args=(context, requests, refreshtime),
                                  name=f"Worker thread {i}")
        thread.start()
        worker_threads.append(thread)
        time.sleep(thread_creation_delay)


def main(
        file: Optional[typer.FileText] = typer.Argument(None,
                                                        help='Path to file containing a cURL command to run. Will use clipboard value if not provided. \033[1mMust only contain a single valid cURL command!\033[0m'),
        requests: int = typer.Option(DEFAULT_REQUESTS, "--requests", "-r", help='Number of times to run cURL command.', min=1),
        threads: int = typer.Option(DEFAULT_THREADS, "--threads", "-t",
                                    help='Number of threads to run cURL commands in parallel.', min=1),
        thread_creation_delay: int = typer.Option(DEFAULT_THREAD_CREATION_DELAY, "--delay", "-d",
                                    help='Delay between creation of worker threads.', min=0),
        refreshtime: int = typer.Option(DEFAULT_REFRESHTIME, "--refreshtime",
                                        help='Number of seconds between cURL commands.', min=0),
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
    print(f"{'URL:':<25}{context.url}")
    print(f"{'Request amount:':<25}{requests}")
    print(f"{'Threads:':<25}{threads}")
    print(f"{'Thread creation delay:':<25}{thread_creation_delay}")
    print(f"{'App name:':<25}{appname}")
    print(f"{'Comments':<25}{comment}")
    print(f"{'Refresh time:':<25}{refreshtime}")
    print("=" * 40)

    start_threads(context, requests, refreshtime, threads, thread_creation_delay)

    # wait for all threads to finish
    for t in worker_threads:
        t.join()

    # TODO saving data etc...


if __name__ == "__main__":
    typer.run(main)


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
