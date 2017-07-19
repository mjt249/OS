from threading import Thread, Semaphore

def P(sema):
    sema.acquire()

def V(sema):
    sema.release()

class Add(Thread):

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        for j in range(10000):
            for i in range(10):
                matrix[i] = matrix[i] + 1

class Sub(Thread):

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        for j in range(10000):
            for i in range(10):
                matrix[i] = matrix[i] - 1


matrix = [90, 90, 90, 90, 90, 90, 90, 90, 90, 90]

a = Add()
s = Sub()

a.start()
s.start()

a.join()
s.join()

print(matrix)


## vim: et ai ts=4 sw=4

