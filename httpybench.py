#!/usr/bin/env python3
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
from tabulate import tabulate
from pyfiglet import Figlet

DEFAULT_REQUESTS = 10
DEFAULT_THREADS = 1
DEFAULT_THREAD_CREATION_DELAY = 0
DEFAULT_REQUEST_DELAY = 5

RESULT_QUEUE = queue.Queue()


def benchmark_worker(context, requests, request_delay):
    url = context.url
    method = context.method
    cookies = context.cookies
    headers = context.headers
    data = context.data
    payload = None
    if data:
        payload = json.loads(data)

    response_times = []
    successes = 0

    for i in range(requests):

        try:
            print(f"[{threading.current_thread().name}] Sending request...")
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

            if response.status_code == 200:
                successes += 1

            print(f"[{threading.current_thread().name}] Recieved response...")
            print(f"[{threading.current_thread().name}] Response status code: {response.status_code}")
            print(f"[{threading.current_thread().name}] Response time: {round(delta_time * 1000)}ms")

        except requests.exceptions.ConnectionError as e:
            print(f"[{threading.current_thread().name}] Connection refused when sending request to {url}")
            print(f"[{threading.current_thread().name}] Error: {e}")

        if requests - i > 1:
            time.sleep(request_delay)

    average_response_time = sum(response_times) / len(response_times)
    median_response_time = statistics.median(response_times)
    success_rate = successes / requests

    if requests > 1:
        result = {
            "Thread Name": threading.current_thread().name,
            "Average response time": average_response_time,
            "Median response time": median_response_time,
            "Fastest response time": min(response_times),
            "Slowest response time": max(response_times),
            "Successful responses": successes,
            "Success rate": success_rate,
            "Response times": response_times
        }
    else:
        result = {
            "Thread Name": threading.current_thread().name,
            "Response time": average_response_time,
            "Successful responses": successes,
            "Success rate": success_rate,
            "Response times": response_times
        }

    RESULT_QUEUE.put(result)

    print(f"[{threading.current_thread().name}] has finished!")


def print_results(benchmark_time):
    print(f"\nBenchmarks finished!")
    print(f"Total benchmark time: {benchmark_time}\n")
    result_list = []

    for result in RESULT_QUEUE.queue:
        result_without_response_times = {key: value for key, value in result.items() if key != "Response times"}
        result_list.append(result_without_response_times)

    if len(result_list) > 1:
        # Calculate the sum of values in the result_list using dictionary comprehension
        sum_results = {k: sum(r[k] for r in result_list) for k in result_list[0] if k != "Thread Name"}

        # Calculate the average of the values in the sum_results and create average_result
        num_results = len(result_list)
        average_result = {"Thread Name": "Average results", **{k: (v / num_results) for k, v in sum_results.items()}}

        result_list.append(average_result)

    for result in result_list:
        result["Success rate"] = f"{result['Success rate'] * 100:.2f}%"
        for key, value in result.items():
            if key not in {"Success rate", "Successful responses", "Thread Name"}:
                result[key] = f"{round(value * 1000)}ms"

    table = tabulate(result_list, headers="keys", tablefmt="grid")
    print(table)


def save_results(benchmark_info, savefile):
    if savefile is None:
        return

    result_list = list(RESULT_QUEUE.queue)
    result_list.insert(0, benchmark_info)

    try:
        with open(savefile, "r+") as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = []

            existing_data.append(result_list)
            f.seek(0)
            json.dump(existing_data, f, indent=4, default=str)
            f.truncate()
    except FileNotFoundError:
        with open(savefile, "w") as f:
            existing_data = [result_list]
            json.dump(existing_data, f, indent=4, default=str)
    finally:
        f.close()


def print_run_info(context, requests, threads, thread_creation_delay, request_delay):
    # Truncate the URL if it's longer than 60 characters
    truncated_url = context.url[:60] + "..." if len(context.url) > 60 else context.url

    table = [
        ["URL:", truncated_url],
        ["Number of requests:", requests],
        ["Worker threads:", threads],
        ["Thread creation delay:", thread_creation_delay],
        ["Time between requests:", request_delay],
    ]

    print(tabulate(table, colalign=["center", "left"], tablefmt="grid"))
    print(f"\nStarting benchmarks...\n")


def run_threads(context, requests, request_delay, number_of_threads, thread_creation_delay):
    worker_threads = []
    for i in range(number_of_threads):
        thread = threading.Thread(target=benchmark_worker, args=(context, requests, request_delay),
                                  name=f"Worker thread {i}")
        thread.start()
        worker_threads.append(thread)
        time.sleep(thread_creation_delay)

    for thread in worker_threads:
        thread.join()


def main(
        file: Optional[typer.FileText] = typer.Argument(None,
                                                        help='Path to file containing a cURL command to run. Will use clipboard value if not provided. \033[1mMust only contain a single valid cURL command!\033[0m'),
        requests: int = typer.Option(DEFAULT_REQUESTS, "--requests", "-r",
                                     help='Number of times to run cURL command on each worker thread.',
                                     min=1),
        threads: int = typer.Option(DEFAULT_THREADS, "--threads", "-t",
                                    help='Number of worker threads to run cURL commands in parallel.', min=1),
        thread_creation_delay: int = typer.Option(DEFAULT_THREAD_CREATION_DELAY, "--delay", "-d",
                                                  help='Delay between creation of worker threads.', min=0),
        request_delay: int = typer.Option(DEFAULT_REQUEST_DELAY, "--request_delay",
                                        help='Number of seconds to sleep between cURL commands.', min=0),
        savefile: str = typer.Option(None, "--savefile", "-s",
                                     help='File to save results in json format. Results will not be saved if omitted.'),

):
    f = Figlet(font='slant')
    print(f.renderText('HttPyBench'))

    if file is None:
        # If not provided with file, get clipboard value
        curl = pyperclip.paste().encode().decode('unicode_escape')
    else:
        # If provided with file, read the contents of the file
        curl = file.read().encode().decode('unicode_escape')

    context = uncurl.parse_context(curl)
    benchmark_info = {
        "Time": datetime.now(),
        "Context": context,
        "Requests": requests,
        "Threads": threads,
        "Creation_delay": thread_creation_delay,
        "Request_delay": request_delay
    }

    print_run_info(context, requests, threads, thread_creation_delay, request_delay)

    before_requests = datetime.now()

    run_threads(context, requests, request_delay, threads, thread_creation_delay)

    after_requests = datetime.now()
    benchmark_time = after_requests - before_requests

    print_results(benchmark_time)
    save_results(benchmark_info, savefile)


if __name__ == "__main__":
    typer.run(main)
