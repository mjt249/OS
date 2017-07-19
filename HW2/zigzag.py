from threading import Thread, Semaphore
import sys

def P(sema):
    sema.acquire()

def V(sema):
    sema.release()

#
# Using semaphores, modify the program below so that it prints the following:
#

result = """
---
   |
   |
    ---
       |
       |
        ---
           |
           |
"""

#
# You may split for loops into multiple loops, but the total number of
# iterations should remain the same.
#

class Dash(Thread):

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        for j in range(9):
            sys.stdout.write("-")

class Vertical(Thread):

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        for i in range(6):
            sys.stdout.write("|")

class NewLine(Thread):

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        for i in range(9):
            sys.stdout.write("\n")

class White(Thread):

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        for i in range(54):
            sys.stdout.write(" ")


if __name__ == "__main__":
    Dash().start()
    Vertical().start()
    NewLine().start()
    White().start()

## vim: et ai ts=4 sw=4

