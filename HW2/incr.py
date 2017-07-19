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
                P(index_matrix_semaphores[i])
                matrix[i] = matrix[i] + 1
                V(index_matrix_semaphores[i])

class Sub(Thread):

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        for j in range(10000):
            for i in range(10):
                P(index_matrix_semaphores[i])
                matrix[i] = matrix[i] - 1
                V(index_matrix_semaphores[i])


matrix = [90, 90, 90, 90, 90, 90, 90, 90, 90, 90]

index_matrix_semaphores = []

for j in range(len(matrix)):
    index_matrix_semaphores.append(Semaphore(1))

a = Add()
s = Sub()

a.start()
s.start()

a.join()
s.join()

print(matrix)


## vim: et ai ts=4 sw=4

