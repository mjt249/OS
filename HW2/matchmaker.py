from threading import Thread, Lock, Condition
import time, random


class Matchmaker(object):
    """
    A matchmaker monitor collects groups of n threads, blocking them until there
    is a complete group available.
    """

    def __init__(self, n):
        self.lock = Lock()
        self.nbr_players_to_start = n
        self.current_number_of_players = 0

        # Predicate: current_number_of_players < nbr_players_to_start
        self.can_be_added = Condition(self.lock)

        # Predicate: current_number_of_players = nbr_players_to_start
        self.can_start_game = Condition(self.lock)

    def join(self):
        """block until a game starts that includes this thread.  If n threads
        are blocked, start a game."""
        with self.lock:
            # If the current game spaces are full, block until space for the next game opens up
            while self.current_number_of_players >= self.nbr_players_to_start:
                self.can_be_added.wait()

            # Add yourself to the pool of players for the current game
            self.current_number_of_players += 1

            # If there are enough players to start, notify the waiting pooled players

            if self.current_number_of_players == self.nbr_players_to_start:
                self.can_start_game.notify_all()

            # Otherwise, wait until there are enough players to start
            else:
                self.can_start_game.wait()

            # Threads here can start the game and notify the players waiting for a pool that the new one
            # has opened
            self.current_number_of_players -= 1
            self.can_be_added.notify_all()

class Player(Thread):
    def __init__(self, matchmaker, name):
        Thread.__init__(self)
        self.matchmaker = matchmaker
        self.id = name

    def run(self):
        # wait a random amount of time
        time.sleep(random.uniform(0.1, 0.5))
        print("Player %i arriving" % self.id)
        self.matchmaker.join()
        print("Player %i playing" % self.id)


if __name__ == '__main__':
    queue = Matchmaker(4)
    for i in range(100):
        Player(queue, i).start()

# vim:expandtab:tabstop=8:shiftwidth=4:softtabstop=4
