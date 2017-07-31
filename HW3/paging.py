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
        self.address_dict = {}

        # Build dictionary of all trace values and occurences
        for i, address in enumerate(trace):
            if address in self.address_dict:
                self.address_dict[address].append(i)
            else:
                self.address_dict[address] = deque()
                self.address_dict[address].append(i)

    def access(self, address):
        self.trace_counter += 1
        return Pager.access(self, address)


    def evict(self):
        if not self.mem_populated:
            self.pointer_to_populate += 1
            if self.pointer_to_populate == (self.num_frames - 1):
                self.mem_populated = True
            return self.pointer_to_populate

        else:
            # Hash has been built.

            # List of size num_frames. Each index is the next use of that address
            # Each index is set to the max in case that address is not used again
            next_use = [sys.maxsize] * self.num_frames
            for i, address in enumerate(self.frames):
                current_dq = self.address_dict[address]


                # Iterates through the queue and pops occurences less than the current trace position
                while len(current_dq) > 0 and current_dq[0] <= self.trace_counter:
                    current_dq.popleft()

                if len(current_dq) > 0:
                    next_use[i] = current_dq[0]

            # In the form (index in frames, next index of address use in trace)
            ind_to_evict = (0,0)
            for i, next_ind in enumerate(next_use):
                if next_ind > ind_to_evict[1]:
                    ind_to_evict = (i, next_ind)
            return ind_to_evict[0]



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
