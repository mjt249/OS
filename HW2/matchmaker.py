from threading import Thread, Lock, Condition
import time, random

class Matchmaker(object):
    """
    A matchmaker monitor collects groups of n threads, blocking them until there
    is a complete group available.
    """

    def __init__(self, n):
        # TODO
        pass

    def join(self):
        """block until a game starts that includes this thread.  If n threads
        are blocked, start a game."""
        # TODO
        pass

class Player(Thread):
    def __init__(self, matchmaker, name):
        Thread.__init__(self)
        self.matchmaker = matchmaker
        self.id = name

    def run(self):
        # wait a random amount of time
        time.sleep(random.uniform(0.1,0.5))
        print("Player %i arriving" % self.id)
        self.matchmaker.join()
        print("Player %i playing" % self.id)

if __name__ == '__main__':
    queue = Matchmaker(4)
    for i in range(100):
        Player(queue, i).start()

# vim:expandtab:tabstop=8:shiftwidth=4:softtabstop=4 
