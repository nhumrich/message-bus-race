#!/bin/env python2
import requests
import time
import matplotlib.pyplot as plt
import multiprocessing
from simplejson.scanner import JSONDecodeError


def make_and_log_request(path):
    start = time.time()
    response = requests.get('http://127.0.0.1:8080' + path)

    try:
        json_response = response.json()
    except JSONDecodeError as e:
        print("code: {} port: {} message: {}".format(
            response.status_code,
            path,
            response.content
        ))
        return -5000, -50

    end = time.time()
    return json_response['message'].__sizeof__(), (end - start)*1000


def plot_it(plots, save_location):
    plt.figure()
    plt.scatter(*zip(*plots[0]), c='b', label='nats')
    plt.scatter(*zip(*plots[1]), c='r', label='http')
    plt.scatter(*zip(*plots[2]), c='g', label='rabbit')

    plt.legend(loc='lower right')
    plt.ylabel('round-trip time (ms)')
    plt.xlabel('message size (bytes)')

    plt.savefig(save_location)


def run_one_at_a_time():
    plots = []
    for path in ('/nats', '/http', '/rabbit'):
        plot_list = []
        plots.append(plot_list)
        for i in range(200):
            size, rt_time = make_and_log_request(path)
            plot_list.append((size, rt_time))

    plot_it(plots, '../results/one-at-a-time.png')


def worker(port):
    print('out')
    result = make_and_log_request(port)
    print('in')
    return result


def many_users_at_a_time():
    plots = []

    for path in ('/nats', '/http', '/rabbit'):
        jobs = [path for i in range(200)]
        pool = multiprocessing.Pool(processes=10)
        plot_list = pool.map(worker, jobs)
        plots.append(plot_list)

    plot_it(plots, '../results/multiple-users.png')


if __name__ == "__main__":
    run_one_at_a_time()
    many_users_at_a_time()
