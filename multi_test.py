




from threading import Thread
import time
from collections import deque


def print_content(d):
    while True:
        #print(d)
        if len(d) > 0:
           print(d[-1])
        time.sleep(0.5)

# def write_content(d):



if __name__ == "__main__":
    d = deque()
    p = Thread(target=print_content, args=(d,))
    p.start()
    for i in range(1000):
        d.append(i)
        time.sleep(0.01)