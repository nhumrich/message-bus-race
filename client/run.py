#!/bin/env python2
import requests
import time
import matplotlib.pyplot as plt

# test 1, single user

plots = []

for port in ('8888', '8887'):
    plot_list = []
    plots.append(plot_list)
    for i in range(200):
        start = time.time()
        response = requests.get('http://127.0.0.1:' + port).json()
        end = time.time()
        if response['message'].__sizeof__() > 150000:
            print(response['message'].__sizeof__())
        plot_list.append((response['message'].__sizeof__(), (end - start)*1000))


plt.scatter(*zip(*plots[0]), c='b', label='nats')
plt.scatter(*zip(*plots[1]), c='r', label='http')
plt.legend(loc='upper right')
plt.ylabel('round-trip time (ms)')
plt.xlabel('message size (bytes)')
plt.show()


# test 2, multiple users
