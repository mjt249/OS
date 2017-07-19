"""A simulation for experimenting with multiple threads and processes"""

from threading import Thread
import time
import sys
import random
from subprocess import Popen


################################################################################
## unit of work ################################################################
################################################################################

def do_step(i):
    """simulates a task that requires a bit of processing and some I/O"""
    for j in range(1000):
        random.seed(i)
        val = random.gauss(0, 2)

    random.seed(i)
    val = random.gauss(0, 2)
    if (val > 1):
        return 1
    else:
        return 0


def do_steps(k, n, N):
    """given N units of work divided into n batches, performs the kth batch (k is
       in the range [kN/n,(k+1)N/n)."""
    start = int(k * N / n)
    finish = int(min((k + 1) * N / n, N))

    value = 0
    for i in range(start, finish):
        value += do_step(i)
    return value


################################################################################
## sequential implementation ###################################################
################################################################################

def run_sequential(N):
    """perform N steps sequentially"""
    return do_steps(0, 1, N)


################################################################################
## threaded implementation #####################################################
################################################################################

class ThreadedWorker(Thread):
    def __init__(self, k, n, N):
        """initialize this thread to be the kth of n worker threads"""
        Thread.__init__(self)
        self.k = k
        self.n = n
        self.N = N
        self.result = None

    def run(self):
        """execute the worker thread's work"""
        self.result = do_steps(self.k, self.n, self.N)


def run_threaded(num_threads, N):
    """use num_thread threads to perform N steps"""
    # TODO: create num_threads workers
    # TODO: run them
    # TODO: collect the results and return their sum
    # Note: use the threading module from the python standard library
    # Note: import threading; help(threading.Thread)
    # Note: be sure that your implementation is concurrent!

    # Create threads, add them to thread_list, and start them running
    thread_list = []
    for i in range(num_threads):
        current_thread = ThreadedWorker(i, num_threads, N)
        current_thread.start()
        thread_list.append(current_thread)

    # Waits for threads to all finish
    for current_t in thread_list:
        current_t.join()

    # Combines result
    value_result = 0
    for current_t in thread_list:
        value_result += current_t.result

    return value_result


################################################################################
## multiprocess implementation #################################################
################################################################################

def create_python_subprocess(args):
    """Start a subprocess running this python file.  The command line arguments
       are given by "args", which should be a sequence of strings.
       For example, calling "create_python_subprocess(['child'])"
       has the same effect as running
       "python parcount.py child" at the command line."""

    return Popen([sys.executable, sys.argv[0]] + args)


def run_multiproc(num_children, N):
    """use num_children subprocesses to perform N steps"""
    # TODO: fork num_children subprocesses to compute the results
    # Note: use the create_python_subprocess function above, which returns a POpen
    #       object.
    #       See https://docs.python.org/3/library/subprocess.html#popen-objects
    #       for documentation on POpen objects
    # Note: the return code of the child processes will the value returned by
    #       run_child (see __main__ below).  You can use this to pass results
    #       from the child back to the parent.  This is an abuse of the exit code
    #       system, which is intended to indicate whether a program failed or not,
    #       but since we're only trying to communicate a single integer from the
    #       child process to the parent, it suits our purposes.
    # Note: be sure that your implementation is concurrent!

    proc_list = []
    for i in range(num_children):
        current_proc = create_python_subprocess(["child", str(i), str(num_children), str(N)])
        proc_list.append(current_proc)

    result = 0
    for proc in proc_list:
        result += proc.wait()
    return result



def run_child(k, n, N):
    """do the work of a single subprocess"""
    # TODO: do the work for the ith (of n) children
    return do_steps(k, n, N)



################################################################################
## program main function #######################################################
################################################################################

def usage():
    print("""
expected usage:
  %s %s <args>

where <args> is one of:
  sequential
  threaded  <num_threads>
  multiproc <num_subprocesses>
  child     <arguments up to you>
""" % (sys.executable, sys.argv[0]))
    return -1


if __name__ == '__main__':
    """parse the command line, execute the program, and print out elapsed time"""
    N = 100
    start_time = time.time()

    if len(sys.argv) <= 1:
        sys.exit(usage())
    command = sys.argv[1]

    if command == "sequential":
        print(run_sequential(N))

    elif command == "threaded":
        if len(sys.argv) <= 2:
            sys.exit(usage())
        print(run_threaded(int(sys.argv[2]), N))

    elif command == "multiproc":
        if len(sys.argv) <= 2:
            sys.exit(usage())
        print(run_multiproc(int(sys.argv[2]), N))

    elif command == "child":
        # Note: this is an abuse of the exit status indication
        sys.exit(run_child(int(sys.argv[2]), int(sys.argv[3]), N))

    else:
        sys.exit(usage())

    print("elapsed time: ", time.time() - start_time)
