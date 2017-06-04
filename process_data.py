import os
from multiprocessing import Manager
from multiprocessing.pool import Pool
from time import sleep

import pandas as pd

from distance_meter import DistanceMeter

DATA_DIRECTORY = "data"
OUTPUT_DIRECTORY = "results"


class Worker:
    MAX_SANE_VELOCITY = 80  # there are weird records in collected data
    REPORTING_FREQUENCY = 1e4

    def __init__(self, queue, filename, output_directory):
        self.queue = queue
        self.filename = filename
        self.output_directory = output_directory
        self.distance_meter = DistanceMeter()
        self.df = pd.read_json(filename)
        self.REPORTING_FREQUENCY = int(len(self.df)/1000)
        self.df.sort_values(["first_line", "brigade", "time"], inplace=True)
        self.run()
        self.save()
        self.queue.put((len(self.df), len(self.df)))  # inform that it's done

    def run(self):
        velocities = [None]
        zipped_rows = zip(
            self.df[1:].itertuples(False), self.df.itertuples(False))
        nrows = len(self.df)
        for i, (row2, row1) in enumerate(zipped_rows):
            velocities.append(self.calculate_velocity(row2, row1))
            if (i + 1) % self.REPORTING_FREQUENCY == 0:
                self.queue.put((i + 1, nrows))
        self.df["velocity"] = pd.Series.from_array(velocities).values

    def calculate_velocity(self, row2, row1):
        if row1.first_line != row2.first_line or row1.brigade != row2.brigade:
            return None
        dist = self.distance_meter.get_distance_between_coords(
            row1.latitude, row1.longtitude, row2.latitude, row2.longtitude,
            str(row2.first_line))
        time = (row2.time - row1.time) or None
        if dist and time:
            velocity = dist / (time / (1000 * 60 * 60))
            return velocity if velocity < self.MAX_SANE_VELOCITY else None

    def save(self):
        self.df = self.df[self.df.velocity.notnull()]
        filename, _ = os.path.splitext(os.path.split(self.filename)[-1])
        output_filename = os.path.join(
            self.output_directory, "{}.csv".format(filename))
        self.df.to_csv(output_filename, index=False)


def invoke_worker(queue, filename, output_directory):
    """
    unpack Pool.map iterable argument and pass it to new worker instance;
    return True when it finish
    that's not the cleanest solution, but it works well
    """
    Worker(queue, filename, output_directory)
    return True


def show_progress(queues, progress_array):
    PROGRESS_BAR_LENGTH = 60

    for i, queue in enumerate(queues):
        progress = progress_array[i]
        while not queue.empty():
            done, total = queue.get_nowait()
            progress = done / total
        progress_array[i] = progress

    os.system("clear")
    for i, progress in enumerate(progress_array):
        print("Worker {}:".format(i))
        print("{:5.1f}%  |{}{}|".format(
            progress * 100,
            int(progress * PROGRESS_BAR_LENGTH) * "#",
            (PROGRESS_BAR_LENGTH - int(progress * PROGRESS_BAR_LENGTH)) * "-"
        ))


if __name__ == "__main__":
    files = [os.path.join(DATA_DIRECTORY, f) for f in
             os.listdir(DATA_DIRECTORY)]
    manager = Manager()
    queues = [manager.Queue() for f in files]
    progress = [0 for f in files]
    worker_args = [(q, f, OUTPUT_DIRECTORY) for q, f in zip(queues, files)]
    if not os.path.exists(OUTPUT_DIRECTORY):
        os.makedirs(OUTPUT_DIRECTORY)
    with Pool() as p:
        rs = p.starmap_async(invoke_worker, worker_args, chunksize=1)
        while not rs.ready():
            show_progress(queues, progress)
            sleep(5)
        show_progress(queues, progress)
        print("Bye!")
