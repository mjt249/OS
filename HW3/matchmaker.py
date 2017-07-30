from threading import Thread, Lock, Condition
import time, random

class MinimalUnfairMatchmaker(object):
    """
    A matchmaker monitor collects groups of n threads, blocking them until there
    is a complete group available.
    """

    def __init__(self, n):
        self.lock = Lock()
        self.in_lobby = 0 # number of unadmitted threads
        self.admitted = 0 # number of admitted threads
        self.n        = n

        self.can_go = Condition(lock) # predicate: self.admitted > 0

    def join(self):
        with self.lock:
            self.in_lobby += 1

            if self.in_lobby == self.n:
                self.in_lobby -= self.n
                self.admitted += self.n

            while not (self.admitted > 0):
                self.can_go.wait()

            self.admitted -= 1

class MinimalFullCreditMatchmaker(object):
    """
    A matchmaker monitor collects groups of n threads, blocking them until there
    is a complete group available.
    """

    def __init__(self, n):
        self.lock = Lock()
        self.in_lobby  = 0 # number of unadmitted threads
        self.next_game = 0 # the next game that will start

        self.can_go = Condition(lock) # predicate: self.next_game > [local game]

    def join(self):
        with self.lock:
            self.in_lobby += 1
            game = self.generation

            if self.in_lobby == self.n:
                self.in_lobby  = 0
                self.next_game += 1

            while not (self.next_game > game):
                self.can_go.wait()


################################################################################
## below are proofs of correctness for the unfair and fair matchmakers        ##
################################################################################

class UnfairMatchmaker(object):
    """
    A matchmaker monitor collects groups of n threads, blocking them until there
    is a complete group available.

    Recall that a safety property is the absence of a bad thing happening.  In
    this case, the bad thing is if too many threads leave join: enough that some
    of them can't form a group.  Formally: if at any point 'num_threads'
    threads have called join, then at most n*floor(num_threads/n) have returned.
    """

    def __init__(self, n):
        """create a matchmaker that admits groups of n players.
        precondition: n > 0"""

        self.lock = Lock()

        self.in_lobby = 0 # the number of threads that have called join but have
                          # not been allowed to proceed

        self.admitted = 0 # the number of threads that have been mathed but have
                          # not left join

        self.can_go   = Condition(self.lock) # predicate: self.admitted > 0

        # these variables aren't needed for the operation, but make talking about
        # the invariants easier:

        # self.have_joined = 0 # the number of threads that have ever called join
        # self.have_left   = 0 # the number of threads that have ever returned

        # invariant 1: in_lobby + admitted + have_left = have_joined
        # invariant 2: 0 ≤ in_lobby < n
        # invariant 3: admitted + have_left is a multiple of 4
        # invariant 4: all variables are non-negative

        # note: all invariants hold here

    def join(self):
        with self.lock:
            # we can assume all invariants, since they are true when we exit
            # or wait.  But a thread joins:

            # self.have_joined += 1

            # so we have to reestablish invariant 1:
            self.in_lobby += 1

            # but that violates invariant 2, so we fix it (while preserving other invariants):
            if self.in_lobby is self.n:
                self.in_lobby -= self.n
                self.admitted += self.n
                self.can_go.notifyAll()

            # all invariants hold here.  We want to decrement have_left, but
            # doing so would violate invariants so we must wait

            while not (self.admitted > 0):
                self.can_go.wait()

            # thread is about to leave:
            # self.have_left += 1

            # so we need to reestablish invariant 1.  Note that this preserves
            # invariant 4 because we know admitted > 0
            self.admitted -= 1

            # proof of safety: we want to show has_left ≤ n*floor(has_joined / n)
            #
            #   by invariant 1, has_left + in_lobby + admitted = has_joined
            #   so has_left + admitted = has_joined - in_lobby ≤ has_joined
            #   (since in_lobby >= 0 by invariant 4).
            #
            #   Dividing by n, we have (has_left + admitted)/n ≤ has_joined/n.
            #   But has_left + admitted is a multiple of n, so
            #   (has_left + admitted) / n is an integer; since it is less
            #   than or equal to has_joined/n, it must also be less than or
            #   equal to the floor of has_joined/n.

class Matchmaker(object):
    """This has the same specification as UnfairMatchmaker, but prevents threads
    from leaving before threads that were grouped before they entered.
    """

    # note: I do not prove fairness here, only safety.  Specifying and proving
    #       fairness requires theoretical tools that are beyond the scope of
    #       this course.  Also, it's pretty clearly fair, because the game
    #       number never goes down.

    def __init__(self, n):
        self.lock = Lock()
        self.n             = n
        self.in_lobby      = 0 # number of unadmitted threads
        self.started_games = 0 # number of games that have been started
        self.can_go        = Condition(self.lock) # predicate: generation > [local generation]

        # additional variables for specification:
        # self.have_joined = 0 # number of threads that have called join
        # self.have_left   = 0 # number of threads that have returned from join
        # self.joining[i]  = 0 # number of threads with executing join with local game == i

        # invariant 1:  have_joined = sum(joining) + have_left
        # invariant 2:  in_lobby < n
        # invariant 3:  have_left + sum(joining) = started_games * n + in_lobby
        # invariant 4:  joining[started_games] = in_lobby
        # invariant 5:  joining[g] = 0 if g > started_games

    def join(self):
        with self.lock:
            # at this point, all invariants hold, but then we add a thread
            # so we must increment joining and have_joined

            game = self.started_games

            # self.have_joined   += 1
            # self.joining[game] += 1
            self.in_lobby += 1

            # at this point, all invariants but 2 hold

            if self.in_lobby == self.n:
                # establish invariant 2
                self.in_lobby      -= self.n

                # establish invariant 3
                self.started_games += 1
                self.released.notify_all()

                # invariant 4 holds: the current value of started_games is now
                # larger than the value of started_games before the increment,
                # so by invariant 5, it is 0; and we have just set self.in_lobby
                # to 0.

            # at this point, all invariants hold.  But we can't safely increment
            # has_left without waiting:

            while not self.started_games > game:
                self.released.wait()

            # invariants hold here.  the thread is about to exit:

            # joining[game] -= 1
            # has_left      += 1

            # invariants 1 and 3 are preserved because have_left +
            # sum(joining) is unchanged.  invariant 2 is
            # unaffected.  invariants 4 and 5 vacuously hold
            # because game ≠ started_games and g < started_games

            # proof of safety: we want to show have_left ≤ n * floor(has_joined / n)
            #
            #   since 0 ≤ in_lobby < n (invariant 2), we have
            #      n * floor(have_joined / n) = floor(started_games + in_lobby/n)
            #                                 = n * started_games
            #
            #   We also know that joining[started_games] = in_lobby, so
            #   sum(joining) ≥ in_lobby; therefore in_lobby - sum(joining) ≤ 0
            #
            #   Putting these together, we have
            #      have_left = n*started_games + in_lobby - sum(joining)
            #                    [by invariant 3]
            #                ≤ n*started_games
            #                    [since in_lobby - sum(joining) ≤ 0]
            #                = n*floor(have_joined/n)
            #                    [by above]
            #   which is what we wanted to prove.


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
