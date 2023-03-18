from reader import Reader
from scheduler import *
from exception import WrongOption


def main():

    reader = Reader()
    print(f"Menu:\n"
          f"  1. Read file -> show scheduling\n"
          f"  2. Read file -> print machines and part\n"
          f"  3. Exit\n")
    while True:
        try:
            option = input("Choose option: ")

            if option == "1":
                path = input("Enter file: ")

                machines, parts = reader.read_file(path)
                scheduler = Scheduler(machines, parts)
                scheduler.create_conjunctive_arcs()
                scheduler.create_disjunctive_arcs()
                # print(scheduler.get_overall_time())
                scheduler.print_machine_executions()

            elif option == "2":
                path = input("Enter file:")

                machines, parts = reader.read_file(path)

                print("\nMachines:")
                for m in machines:
                    print(m)
                print("Parts:")
                for p in parts:
                    print(p)

            elif option == "3":
                exit()

            else:
                raise WrongOption()

        except WrongOption as e:
            print("\n\033[31m" + e.message + "\033[0m\n")
        except FileNotFoundError:
            print("\n\033[31mFile not found.\033[0m\n")


if __name__ == '__main__':
    main()

