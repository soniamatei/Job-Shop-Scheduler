from reader import Reader
from scheduler import *


def main():
    reader = Reader()
    machines, parts = reader.read_file("Input_One.txt")

    scheduler = Scheduler(machines, parts)
    scheduler.create_conjunctive_arcs()
    scheduler.create_disjunctive_arcs()
    # print(scheduler.get_overall_time())
    scheduler.print_machine_executions()


if __name__ == '__main__':
    main()

