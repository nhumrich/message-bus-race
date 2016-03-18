import numpy
import random
import string

STANDARD_DEVIATION_VALUE = 2
DISTRIBUTION_CENTER = 5


def get_message_size_range():
    n = 2
    # Repeats until a number within the scale is found.
    while True:
        num = numpy.random.normal(loc=DISTRIBUTION_CENTER, scale=STANDARD_DEVIATION_VALUE)

        if abs(DISTRIBUTION_CENTER-num) <= (STANDARD_DEVIATION_VALUE * n):
            break
    d = {
        # The goal here is that 10000 should be the average
        # And small messages are more likely than large messages
        1: (250, 1999),
        2: (2000, 4499),
        3: (4500, 7999),
        4: (8000, 9999),
        5: (10000, 11999),
        6: (12000, 39999),
        7: (40000, 89999),
        8: (90000, 150000)
    }
    return d[int(num)]


def get_message_size(range):
    min, max = range
    return int(random.uniform(min, max))


def get_message():
    byte_size = get_message_size(get_message_size_range())
    num_of_chars = byte_size - 37
    msg = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(num_of_chars)])
    return msg


def main():
    """
    Used for graphing distributions only.
    If you run just this file, you will get a graph showing you a histogram of message sized
    generated.
    """
    plot = []
    for i in range(500):  # Change the range here to generate more/less examples
        msg = get_message()
        plot.append(msg.__sizeof__())

    import matplotlib.pyplot as plt
    plt.hist(plot, bins=50)
    plt.ylabel('distribution')
    plt.show()


if __name__ == '__main__':
    main()




