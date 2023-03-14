import reader
from scheduler import *


def main():
    machines, parts = reader.read_file("Input_Two.txt")
    for m in machines:
        print(m)
    for p in parts:
        print(p)

    # scheduler = Scheduler(machines, parts)
    # scheduler.create_conjunctive_arcs()
    # scheduler.create_disjunctive_arcs()
    # print(scheduler.get_overall_time())


if __name__ == '__main__':
    main()

