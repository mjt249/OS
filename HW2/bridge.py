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
        self.current_direction = 0
        self.cars_on_bridge = 0

        # # predicate: current_direction = 0
        # self.direction_north = Condition(self.lock)
        #
        # # predicate: current_direction = 1
        # self.direction_south = Condition(self.lock)
        # # predicate: current_direction == direction
        # self.correct_direction = Condition(self.lock)
        # # predicate cars_on_bridge = 0
        # self.no_cars_on_bridge = Condition(self.lock)

        #predicate not current_direction = direction and cars_on_bridge = 0
        self.ready_for_switch = Condition(self.lock)

    """wait for permission to cross the bridge.  direction should be either
    north (0) or south (1)."""
    def cross(self, direction):
        with self.lock:
            while (direction != self.current_direction) and (self.cars_on_bridge > 0):
                self.ready_for_switch.wait()
            print("cars on bridge")
            print(self.cars_on_bridge)
            print("direction")
            print(self.current_direction)
            print("my direction")
            print(direction)
            self.current_direction = direction
            self.cars_on_bridge += 1

    def finished(self):
        with self.lock:
            self.cars_on_bridge -= 1
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
        print("started")
        # request permission to cross
        self.bridge.cross(self.direction)
        print("crossing")
        # drive across
        time.sleep(0.01)

        # signal that we have finished crossing
        self.bridge.finished()
        print("Done")


if __name__ == "__main__":

    judd_falls = OneLaneBridge()
    for i in range(100):
        Car(judd_falls).start()

# vim:expandtab:tabstop=8:shiftwidth=4:softtabstop=4
