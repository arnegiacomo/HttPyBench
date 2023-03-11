# HttPyBench - Benchmark your HTTP applications response times
___
## Description
___
A simple yet customisable CLI-based python script to benchmark cURL commands to your web applications. Uses 
[uncurl](https://github.com/spulec/uncurl) to parse cURL commands to python requests. 

Pass a file containing a cURL command as an argument, and the script will handle the rest. If omitted, it will use the 
value stored in your clipboard.

## Example
___

```bash
$ python httpybench.py example_curl.txt
```

### Result:

```console
+-----------------+-------------------------+------------------------+--------------------+--------------------+------------------------+----------------+
| Thread          |   Average response time |   Median response time |   Fastest response |   Longest response |   Successful responses | Success rate   |
+=================+=========================+========================+====================+====================+========================+================+
| Worker thread 0 |                0.458962 |               0.458065 |           0.453733 |           0.468245 |                     10 | 100.0%         |
+-----------------+-------------------------+------------------------+--------------------+--------------------+------------------------+----------------+
```

## Usage
___
```bash
$ python httpybench.py --help
```

```console
Usage: httpybench.py [OPTIONS] [FILE]

Arguments:
  [FILE]  Path to file containing a cURL command to run. Will use clipboard
          value if not provided. Must only contain a single valid cURL
          command!

Options:
  -r, --requests INTEGER RANGE  Number of times to run cURL command on each worker thread.
                                [default: 10; x>=1]
  -t, --threads INTEGER RANGE   Number of worker threads to run cURL commands in
                                parallel.  [default: 1; x>=1]
  -d, --delay INTEGER RANGE     Delay between creation of worker threads.
                                [default: 0; x>=0]
  --refreshtime INTEGER RANGE   Number of seconds between cURL commands.
                                [default: 5; x>=0]
  -n, --name TEXT               Name of application.
  -c, --comment TEXT            Optional comments.
  -s, --savefile TEXT           File to save results in json format. Results
                                will not be saved if omitted.
  --help                        Show this message and exit.
 ```

## Disclaimer
___
This is not meant as a Denial Of Service tool, it would be a pretty bad one at that... It's basically meant to be an
easy-to-use tool to benchmark endpoints for your applications, e.g. for testing microservices running locally. 