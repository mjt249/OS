from collections import deque
import random
import sys
from threading import Thread, Semaphore

# ###############################################################################
# Shared paging simulation infrastructure #####################################
################################################################################

class Pager(object):
    """Pager objects implement page replacement strategies.  A program can call
       pager.access(addr) to indicate that the given address is being accessed;
       the Pager will ensure that that page is loaded and return the corresponding
       frame number.

       The Pager keeps track of the number of page faults."""

    def __init__(self, num_frames):
        self.page_faults = 0
        self.frames = [None for i in range(num_frames)]
        self.num_frames = num_frames

    def evict(self):
        """return the frame number of a page to be evicted."""
        # This will be implemented in your subclasses below.
        raise NotImplementedError

    def access(self, address):
        """loads the page containing the address into memory and returns the
        frame number of the loaded page."""

        page_num = address
        if page_num in self.frames:
            # hit
            return self.frames.index(page_num)
        else:
            # fault
            self.page_faults += 1
            index = self.evict()
            self.frames[index] = page_num
            return index


################################################################################
# Paging algorithm implementations ############################################
################################################################################

class FIFO(Pager):
    def __init__(self, num_frames):
        Pager.__init__(self, num_frames)
        self.head = 0
        # TODO

    def access(self, address):
        # TODO: you may wish to do additional bookkeeping here.
        return Pager.access(self, address)

    def evict(self):
        evictee = self.head
        #Update pointer to next added
        if self.head == (self.num_frames - 1):
            self.head == 0
        else:
            self.head += 1
        return evictee

# I will implement this with a Deque. I will first populate the deque.
# Then, when a page is accessed, I will move it to the top of the deque. When a page needs to be evicted
# I will take the one at the bottom of the deque.
class LRU(Pager):
    def __init__(self, num_frames):
        Pager.__init__(self, num_frames)
        self.deque_populated = False
        self.dq = deque()
        self.pointer_to_populate = -1
        self.index_to_remove = 0

    def access(self, address):
        if address in self.dq:
            self.dq.remove(address)
            self.dq.append(address)
        else:
            if self.deque_populated:
                address_to_remove = self.dq.popleft()

                # Set variable so evict knows which to return
                self.index_to_remove = self.frames.index(address_to_remove)
                self.dq.append(address)
            else:
                self.dq.append(address)

        return Pager.access(self, address)

    # If deque isn't fully populated, no need to actually evict. Otherwise pop_left
    def evict(self):
        if not self.deque_populated:
            self.pointer_to_populate += 1
            if self.pointer_to_populate == (self.num_frames - 1):
                self.deque_populated = True
            return self.pointer_to_populate
        else:
            return self.index_to_remove


class Random(Pager):
    def __init__(self, num_frames):
        Pager.__init__(self, num_frames)
        self.mem_populated = False
        self.pointer_to_populate = -1

    def access(self, address):
        # TODO: you may wish to do additional bookkeeping here.
        return Pager.access(self, address)

    def evict(self):
        if not self.mem_populated:
            self.pointer_to_populate += 1
            if self.pointer_to_populate == (self.num_frames - 1):
                self.mem_populated = True
            return self.pointer_to_populate
        else:
            return random.randint(0, (self.num_frames - 1))


class OPT(Pager):
    def __init__(self, num_frames, trace):
        """trace is a list of addresses; the full trace of accesses that will be
           performed"""
        Pager.__init__(self, num_frames)
        self.trace_counter = -1
        self.mem_populated = False
        self.pointer_to_populate = -1
        self.hash_built = False
        self.address_dict = {}

    def access(self, address):
        #print("access")
        self.trace_counter += 1
        return Pager.access(self, address)


    def evict(self):
        if not self.mem_populated:
            self.pointer_to_populate += 1
            if self.pointer_to_populate == (self.num_frames - 1):
                self.mem_populated = True
                return self.pointer_to_populate
            if not self.hash_built:
                print("evict")
                for i, address in enumerate(trace):
                    if i % 10000 == 1:
                        print(i)
                    if address in self.address_dict:
                        self.address_dict[address].append(i)
                    else:
                        self.address_dict[address] = deque()
                        self.address_dict[address].append(i)
                self.hash_built = True

                print("finished!")
            return 0
        else:
            # Hash has been built.

            # List of size num_frames. Each index is the next use of that address
            # Each index is set to the max in case that address is not used again
            next_use = [len(trace) + 1] * self.num_frames
            for i, address in enumerate(self.frames):
                current_dq = self.address_dict[address]
                start_length = len(current_dq)
                if not start_length == 0:
                    for ind in range(start_length):
                        if not  len(self.address_dict[address]) == 0:
                            if current_dq[ind] > self.trace_counter:
                                self.address_dict[address].popleft()
                            else:
                                next_use[i] = self.address_dict[address].popleft()

            # In the form (index in frames, next index of address use in trace)
            ind_to_evict = (0,0)
            for i, next_ind in enumerate(next_use):
                if next_ind > ind_to_evict[1]:
                    ind_to_evict = (i, next_ind)
            return ind_to_evict[0]





        #     number_of_threads = self.num_frames / 3
        #     ind_to_evict = run_threaded(number_of_threads, self.num_frames, self.frames, self.trace_counter, len(trace))
        #     return ind_to_evict[0]

###########################################################################################


# def do_step(address, current_trace, trace_size):
#     first_instance = -1
#     for j in range(current_trace, len(trace)):
#         if address == trace[j]:
#             first_instance = j
#             pass
#     if first_instance == -1:
#         return (trace_size + 1)
#     else:
#         return first_instance
#
#
#
#
# def do_steps(k, n, N, frames, current_trace, trace_size):
#     """given N units of work divided into n batches, performs the kth batch (k is
#        in the range [kN/n,(k+1)N/n)."""
#     start = int(k * N / n)
#     finish = int(min((k + 1) * N / n, N))
#
#     worst = (0, -1)
#     for i in range(start, finish):
#         first_instance = do_step(frames[i], current_trace, trace_size)
#         if first_instance > worst[1]:
#             worst = (i, first_instance)
#     return worst
#
#
# class ThreadedWorker(Thread):
#     def __init__(self, k, n, N, frames, current_trace, trace_size):
#         """initialize this thread to be the kth of n worker threads"""
#         Thread.__init__(self)
#         self.k = k
#         self.n = n
#         self.N = N
#         self.frames = frames
#         self.current_trace = current_trace
#         self.trace_size = trace_size
#
#
#     def run(self):
#         global common_result
#         """execute the worker thread's work"""
#         self.result = do_steps(self.k, self.n, self.N, self.frames, self.current_trace, self.trace_size)
#         common_result_sema.acquire()
#         if self.result[1] > common_result[1]:
#             common_result = self.result
#         common_result_sema.release()
#
#
# global common_result
# common_result = (0, -1)
# global common_result_sema
# common_result_sema = Semaphore(1)
#
#
# def run_threaded(num_threads, N, frames, current_trace, trace_size):
#     """use num_thread threads to perform N steps"""
#     # TODO: create num_threads workers
#     # TODO: run them
#     # TODO: collect the results and return their sum
#     # Note: use the threading module from the python standard library
#     # Note: import threading; help(threading.Thread)
#     # Note: be sure that your implementation is concurrent!
#
#     # Create shared variable and corresponding semaphore
#
#     # Create threads, add them to thread_list, and start them running
#     thread_list = []
#     for i in range(num_threads):
#         current_thread = ThreadedWorker(i, num_threads, N, frames, current_trace, trace_size)
#         current_thread.start()
#         thread_list.append(current_thread)
#
#     # Waits for threads to all finish
#     for current_t in thread_list:
#         current_t.join()
#
#     return common_result




################################################################################
## Command line parsing and main driver ########################################
################################################################################

if __name__ == '__main__':
    import argparse
    print("main")

    parser = argparse.ArgumentParser(description="simulate various page replacement algorithms")
    parser.add_argument("-s", "--page-size", help="the number of pages",
                        type=int, default=10)
    parser.add_argument("-n", "--num-frames", help="the number of frames",
                        type=int, required=True)
    parser.add_argument("algorithm", choices=["FIFO", "LRU", "Random", "OPT"],
                        help="the replacement strategy to use")
    parser.add_argument("trace",
                        help="the sequence of addresses to access.  Should be a filename containing one address per line.",
                        type=open)
    args = parser.parse_args()

    trace = [int(int(line) / args.page_size) for line in args.trace.readlines()]
    pager = None
    if args.algorithm == "LRU":
        pager = LRU(args.num_frames)
    elif args.algorithm == "FIFO":
        pager = FIFO(args.num_frames)
    elif args.algorithm == "Random":
        pager = Random(args.num_frames)
    elif args.algorithm == "OPT":
        pager = OPT(args.num_frames, trace)

    for addr in trace:
        frame = pager.access(addr)
        assert (pager.frames[frame] == addr)

    print("total page faults: %i" % pager.page_faults)

# vim: ts=2 sw=2 ai et list
