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
        for i in range(3):
            P(Dash_next)
            for j in range(3):
                sys.stdout.write("-")
            V(NewLine_next)


class Vertical(Thread):

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        for i in range(6):
            P(Vertical_next)
            sys.stdout.write("|")
            V(NewLine_next)

class NewLine(Thread):

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        for i in range(9):
            P(NewLine_next)
            sys.stdout.write("\n")
            V(White_next)

class White(Thread):

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        vertical_space_start = 3
        dash_space_start = 4
        for i in range(3):
            for j in range(2):
                P(White_next)
                for k in range(vertical_space_start):
                    sys.stdout.write(" ")
                V(Vertical_next)
            vertical_space_start += 4

            if i < 2:
                P(White_next)
                for k in range(dash_space_start):
                    sys.stdout.write(" ")
                V(Dash_next)
                dash_space_start += 4

if __name__ == "__main__":

    #When these semas are 1, the are finished and the next thread can work
    Dash_next = Semaphore(1)
    Vertical_next = Semaphore(0)
    NewLine_next = Semaphore(0)
    White_next = Semaphore(0)

    Dash().start()
    Vertical().start()
    NewLine().start()
    White().start()

## vim: et ai ts=4 sw=4

