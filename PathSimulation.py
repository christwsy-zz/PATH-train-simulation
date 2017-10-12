"""
Path train Hoboken to 33rd Stree one way ridership simulation.

@author: Yunyi Liu, Siyue Wang {yliu143, swang81}@stevens.edu
"""
import random
import matplotlib.pyplot as plt
import numpy as np
import numpy.random as rnd
import simpy
# pylint: disable=E1101

class Person(object):
    """High level abstraction of a person"""
    def __init__(self):
        self.destination = ""
        self.is_on_train = False

    def get_destination(self, current_station):
        """One should only get off to the later stations"""
        pass

    def decide_get_on(self, cap_ratio):
        """A person will decide if he wants to take the train when the car's capacity is reached"""
        if cap_ratio >= 0.9:
            # if the car is too full, the person will randomly choose to get on the car
            return bool(random.getrandbits(1))
        else:
            self.is_on_train = True
            return True

    def wait(self, time):
        """I can't remember what this does but it sure does something"""
        pass

class Train(object):
    """Abstract of a train"""
    def __init__(self):
        self.car_capacity = 7 * 35 + 7 * 40 + 0. # contains 7 cars
        self.current_capaicity = 0.
        self.riders = []
        self.is_at_station = False # true if the train is moving to the next station
        self.next_destination = None

    def load(self, rider):
        """If the car is not totally full, we can still load passengers"""
        if self.current_capaicity < self.car_capacity:
            cap_ratio = self.current_capaicity / self.car_capacity
            if rider.decide_get_on(cap_ratio):
                self.riders.append(rider)
            return True
        else:
            return False

    def drop(self, current_station):
        """Drop those who arrive their destinations"""
        for rider in self.riders:
            if rider.destination is current_station:
                self.riders.remove(rider)

class Station(object):
    """Station class"""
    def __init__(self, name):
        self.name = name
        self.num_people_waiting = 0
        self.current_train = None

    def dispatch_train(self):
        """Let the train go"""
        pass

class Path(object):
    """Abstract of the PATH"""
    def __init__(self, environment, num_trains):
        self.station_names = {"Christopher Street", "9th Street", \
                              "14th Street", "23rd Street", "33rd Street"}
        self.stations = []
        self.inter_arrival = 10 # default inter-arrival time between trains for a station
        for station_name in self.station_names:
            self.stations.append(Station(station_name))
        self.env = environment
        self.trains = []
        for _ in range(num_trains):
            self.trains.append(Train)

    def get_inter_arrival(self, time):
        """Get the inter arrival based on the current time"""
        if time < 5 * 60 + 53:
            return 35
        elif time == 5 * 60 + 53:
            return 17
        elif time < 7 * 60 + 10:
            return 10
        else:
            return 10

    def run(self):
        """Path simulation runs for all stations"""
        while True:
            # generate some riders waiting at all stations every minute
            for station in self.stations:
                station.num_people_waiting += self.get_num_riders(station.name, env.now)
            # check if any train arrives
            if env.now % self.inter_arrival == 0:
                for train in self.trains:
                    # self.advance_destination(train)
                    pass
            yield env.timeout(1)

    def remove_train(self):
        """When the train arrives at 33rd st, it waits and go back to hoboken"""
        yield self.inter_arrival
        for station in self.stations:
            if station.name is "33rd Street":
                station.current_train = None

    def get_num_riders(self, station, time):
        """Calculate the number of riders waiting"""
        if station is "33rd Street":
            return time * 70
        elif station is "Christopher Street":
            return time * 10
        else:
            return time * rnd.randint(15, 50)

    def drop(self):
        """Drop riders off if they arrive where they wanna go"""
        for train in self.trains:
            train.drop()

if __name__ == "__main__":
    obs_time = []
    obs_num_trains = []
    obs_riders_geton = []
    obs_riders_getoff = []

    def observe(env, path):
        while True:
            obs_time.append(env.now)
            obs_riders_getoff.append(path)
            obs_riders_geton.append(path)
            yield env.timeout(1)

    np.random.seed(0)
    env = simpy.Environment()
    path = Path(env, 10)
    env.process(path.run())
    env.process(observe(env, path))
    env.run(until=1*60) # run for an hour

    print obs_time