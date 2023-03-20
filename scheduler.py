from time import gmtime


class Vertex:

    def __init__(self, part=None, operation=None, start_time=None, item_number=None):
        self.operation = operation
        self.start = start_time  # start time on the conjunctive part
        self.part = part
        self.item_number = item_number

    def __str__(self):
        if self.part is None:
            return "None"
        return self.part.get_name() + "  " + str(self.item_number) + "  " + self.operation.get_machine().get_name() \
            + "  " + str(self.operation.get_duration()) + "  " + str(self.start)


class Scheduler:

    def __init__(self, machines, parts):
        self.machines = machines
        self.parts = parts
        self.vertices = []
        self.out = {}
        self.start = Vertex()
        self.finish = Vertex()

    @staticmethod
    def get_operation_time(vertex):
        """
        Calculate the time needed to process an operation.
        :param vertex: Vertex
        :return: integer
        """
        return vertex.start + vertex.operation.get_duration() + vertex.operation.get_machine().get_cooldown()

    def create_conjunctive_arcs(self):
        """
        Create arcs between the operations on the same part.
        """
        self.out[self.start] = []
        for part in self.parts:
            # introduce as many 'rows' in the graph as many items of one part are there
            for item_number in range(part.get_no_items()):
                operations = part.get_operations()

                # a variable which sums up the duration of each operation
                # -> this will determine the starting time of each operation
                accumulated_time = 0

                prev = Vertex(part, operations[0], accumulated_time, item_number)
                self.vertices.append(prev)
                self.out[self.start].append(prev)

                for op in operations[1:]:
                    current = Vertex(part, op, accumulated_time, item_number)

                    self.vertices.append(current)
                    self.out[prev] = []
                    self.out[prev].append(current)

                    accumulated_time += op.get_duration()
                    prev = current

                self.out[prev] = []

    def create_disjunctive_arcs(self):
        """
        Create arcs between operations on the same machine.
        """
        for machine in self.machines:
            # get all operations on a specific machine in one list
            vertices_by_machine = list(filter(lambda x: x.operation.get_machine() == machine, self.vertices))

            # make the specific connections between them as follows:
            # t = starting time of the op
            # p = processing time of the op
            # c = cooldown time of the machine
            # t_i + p_i + c <= t_(i+1) + p_(i+1) + c  or  t_(i+1) + p_(i+1) + c <=  t_i + p_i + c
            for index1 in range(len(vertices_by_machine)):
                for index2 in range(index1 + 1, len(vertices_by_machine)):

                    vertex1 = vertices_by_machine[index1]
                    vertex2 = vertices_by_machine[index2]

                    if self.get_operation_time(vertex1) <= self.get_operation_time(vertex2):
                        self.out[vertex1].append(vertex2)

                    elif self.get_operation_time(vertex2) <= self.get_operation_time(vertex1):
                        self.out[vertex2].append(vertex1)

    def order_machines(self):
        """
        Orders the machines in such way that every operation from each part is executed in the right order.
        (ex: a pen which arrives at machine 2 without going trough the 1 first)
        """
        ordered = []

        # this will store indexes of operations list for each part
        # => will help when getting rid of dependencies between machines
        indexes = {}
        for part in self.parts:
            indexes[part] = 0

        # while there is at least one operation unvisited on any part
        ok = False
        while not ok:
            ok = True
            # stores the operation from each part where indexes dict is pointing
            # (the first element from each list which eas not eliminated)
            firsts = []
            for part in self.parts:

                if indexes[part] < len(part.get_operations()):
                    machine = part.get_operations()[indexes[part]].get_machine()
                    # if we didn't took into consideration already this machine
                    if machine not in firsts:
                        ok = False
                        firsts.append(machine)

            for first in firsts:
                is_good = True
                for part in self.parts:
                    for op in part.get_operations()[indexes[part]+1:]:
                        # if we find that a candidate for the independent machine is in any list of operations
                        # from any part => it is dependent (not a good candidate)
                        if first == op.get_machine():
                            is_good = False
                            break

                if is_good:
                    ordered.append(first)
                    for part in self.parts:
                        # go to the next operation for each part that has as its machine, for the current operation index,
                        # the independent one found earlier
                        if part.get_operations()[indexes[part]].get_machine() == first:
                            indexes[part] += 1
                    break

        self.machines = ordered

    def print_machine_executions(self):
        """
        Print the machines execution.
        """
        # order the machines to get rid of any dependency between operations
        self.order_machines()

        # this will denote the finish times for each operation without the cooldown of hte machine
        finish_times = {self.start: 0}

        for machine in self.machines:
            processes = []

            # get all operations on the machine and order them after outdegree (the first to run is the one with
            # the biggest outdegree
            ops_on_machine = list(filter(lambda x: x.operation.get_machine() == machine, self.vertices))
            ops_on_machine = sorted(ops_on_machine, key=lambda x: len(self.out[x]), reverse=True)
            cooldown = machine.get_cooldown()

            i = 0
            j = 0
            # the initial list with processes must be equal with the number of operation on the machine or
            # with the capacity of the machine
            while i < len(ops_on_machine) and j < machine.get_capacity():

                current_operation = ops_on_machine[i]
                parent_of_op = list(filter(lambda x: current_operation in self.out[x], self.out.keys()))[0]

                # initiate the starting time (how long one machine waits until it does the first operation)
                # = the finish time of the parent of the first vertex operation
                # (this is the start from the disjunctive point of view)
                start = finish_times[parent_of_op]
                # add the initial time and duration to find the finish time for the current operation
                finish_times[current_operation] = start + current_operation.operation.get_duration()

                processes.append((current_operation, start))

                i += 1
                j += 1

            print(f"Machine {machine.get_name()}:")

            # set the finish time for each operation on the specific machine
            for next in ops_on_machine[i:]:

                prev_operation, prev_start = min(processes, key=lambda x: finish_times[x[0]])
                # getting the index of the prev_operation means finding in which capacity the operation was done
                index = processes.index((prev_operation, prev_start))

                # next operation begins when current shortest one ends
                start = finish_times[prev_operation]

                conjunctive_parent = list(filter(lambda x: next in self.out[x] and x.part == next.part and
                                                           x.item_number == next.item_number, self.vertices))

                # if the conj parent is not the source node
                if conjunctive_parent:
                    conjunctive_parent = conjunctive_parent[0]

                    # calculate how long a machine waits before receiving another part
                    diff = finish_times[conjunctive_parent] - finish_times[prev_operation]

                    # if dif is > 0 add it to the time before the beginning of next operation
                    if diff > 0:
                        start += diff

                        # see if the cooldown of the machine falls within the time machine has to wait for another part
                        if cooldown - diff > 0:
                            start += cooldown - diff
                    else:
                        start += cooldown
                else:
                    start += cooldown

                finish_times[next] = start + next.operation.get_duration()

                # pop the prev_operation from the process and replace it with the next one
                processes.pop(index)
                processes.insert(index, (next, start))

                # print the operation done (prev_operation)
                start_time = gmtime(prev_start)
                finish_time = gmtime(finish_times[prev_operation])
                print(f"Process {index} => {prev_operation.part.get_name()} ({prev_operation.item_number})  {start_time.tm_hour}:"
                      f"{start_time.tm_min}:{start_time.tm_sec}  ->  {finish_time.tm_hour}:{finish_time.tm_min}:{finish_time.tm_sec} ")

            # print the remaining processes in order of which finishes first
            while processes:
                # find the process which finished first and remove it from the list
                prev_operation, prev_start = min(processes, key=lambda x: finish_times[x[0]])
                index = processes.index((prev_operation, prev_start))
                processes.pop(index)

                start_time = gmtime(prev_start)
                finish_time = gmtime(finish_times[prev_operation])
                print(f"Process {index} => {prev_operation.part.get_name()} ({prev_operation.item_number})  {start_time.tm_hour}:"
                      f"{start_time.tm_min}:{start_time.tm_sec}  ->  {finish_time.tm_hour}:{finish_time.tm_min}:{finish_time.tm_sec} ")

            print()

        final_time = max(finish_times.values())
        final_time = gmtime(final_time)
        print(f"Total time: {final_time.tm_hour}:{final_time.tm_min}:{final_time.tm_sec}\n")