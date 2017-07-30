from threading import Thread, Lock, Condition
import time
import random

north = 0
south = 1


class OneLaneBridge(object):
    """
    A one-lane bridge allows multiple cars to pass in either direction, but at any
    point in time, all cars on the bridge must be going in the same direction.

    Cars wishing to cross should call the cross function, once they have crossed
    they should call finished()
    """

    def __init__(self):
        self.lock = Lock()
        self.current_direction = 0  # Indicates the current direction as either 0 North or 1 South
        self.cars_on_bridge = 0  # Indicates the number of cars currently on the bridge

        self.crossing = [0,0]  # number of threads that have returned from cross(i) but have not yet called finished
        # (here i can be either NORTH or SOUTH).

        # predicate (not current_direction = direction) and (cars_on_bridge = 0)
        # In english, I need to change the direction and there are no cars on the bridge
        self.ready_for_switch = Condition(self.lock)

        # Invariant 1: self.crossing[0] or self.crossing[1] must be 0 at any given time
        # Invariant 2: cars_on_bridge >= 0
        # Invariant 3: current_direction is either 0 or 1


    """
    wait for permission to cross the bridge.  direction should be either
    north (0) or south (1).
    """

    def cross(self, direction):
        with self.lock:
            # While there are cars on the bridge going the opposite direction I want to go in, wait
            while (direction != self.current_direction) and (self.cars_on_bridge > 0):
                self.ready_for_switch.wait()

            # Invariant 3 - When either the direction is the correct one, or there are no cars on the bridge, I can
            # ensure the correct direction and enter the bridge.
            self.current_direction = direction
            # Invariant 2 - This increment can not cause the invariant to become false.
            self.cars_on_bridge += 1
            # To check invarient 1, At this time, the crossing of the opposite of current_direction must be
            # zero because any car that wishes to go the opposite direction is waiting on ready_for_switch().
            # If it passed ready_for_switch, then it has just changed the direction. This can only happen if a
            # notify_all() was called because there were no cars on the bridge going either direction.
            self.crossing[self.current_direction] += 1

    def finished(self):
        with self.lock:
            # To check invarient 1, a car can only get here if it has already incremented crossing, so a decrement
            # can not cause either value of crossing to become less than 0. Neither can it cause either value
            # of crossing to become more than 0 since it is a decrement.

            self.crossing[self.current_direction] -= 1
            # I leave the bridge
            # Invariant 2 - This can only be decremented after a car as finished cross and has already incremented it
            # so it cannot go below 0
            self.cars_on_bridge -= 1

            # If there are no cars on the bridge behind me, I wake up all the cars who are waiting
            # to go in the opposite direction
            # Code is live because if there is no one on the bridge, the cars waiting for ready_for_switch get
            # notify_all and when they regain the monitor lock, they can exit the loop and change the direction to their
            # direction so they can cross
            if self.cars_on_bridge == 0:
                self.ready_for_switch.notify_all()


class Car(Thread):
    def __init__(self, bridge):
        Thread.__init__(self)
        self.direction = random.randrange(2)
        self.wait_time = random.uniform(0.1, 0.5)
        self.bridge = bridge

    def run(self):
        # drive to the bridge
        time.sleep(self.wait_time)

        # request permission to cross
        self.bridge.cross(self.direction)

        # drive across
        time.sleep(0.01)

        # signal that we have finished crossing
        self.bridge.finished()



if __name__ == "__main__":

    judd_falls = OneLaneBridge()
    for i in range(100):
        Car(judd_falls).start()

# vim:expandtab:tabstop=8:shiftwidth=4:softtabstop=4
