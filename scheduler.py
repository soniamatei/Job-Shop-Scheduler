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

    def print_machine_executions(self):
        """
        Print the machines execution.
        """
        print()
        finish_times = {self.start: 0}

        for machine in self.machines:
            # get all operations on the machine and order them after outdegree (the first to run is the one with
            # the biggest outdegree
            ops_on_machine = list(filter(lambda x: x.operation.get_machine() == machine, self.vertices))
            ops_on_machine = sorted(ops_on_machine, key=lambda x: len(self.out[x]), reverse=True)

            current_operation = ops_on_machine[0]
            parent_of_first_op = list(filter(lambda x: current_operation in self.out[x], self.out.keys()))[0]

            # initiate the starting time (how long one machine waits until it does the first operation)
            # = the finish time of the parent of the first vertex operation

            start = finish_times[parent_of_first_op]
            cooldown = machine.get_cooldown()
            # add the initial time and duration to find the finish time for the current operation
            finish_times[current_operation] = start + current_operation.operation.get_duration()

            print(f"{machine.get_name()}:   ", end="")
            # print(f"{current_operation.part.get_name()} ({current_operation.item_number})  start: {start}  "
            #       f"duration: {current_operation.operation.get_duration()}"
            #       f"  finish: {finish_times[current_operation]}s", end=" | ")

            start_time = gmtime(start)
            finish_time = gmtime(finish_times[current_operation])
            print(f"{current_operation.part.get_name()} ({current_operation.item_number})  {start_time.tm_hour}:"
                  f"{start_time.tm_min}:{start_time.tm_sec}  ->  {finish_time.tm_hour}:{finish_time.tm_min}:{finish_time.tm_sec} ",
                  end=" | ")

            # set the finish time for each operation on the specific machine
            for next in ops_on_machine[1:]:

                # next operation begins when current one ends
                # start += current_operation.operation.get_duration()
                start = finish_times[current_operation]

                conjunctive_parent = list(filter(lambda x: next in self.out[x] and x.part == next.part and
                                                           x.item_number == next.item_number, self.vertices))

                # if the conj parent is not the source node
                if conjunctive_parent:
                    conjunctive_parent = conjunctive_parent[0]

                    # calculate how long a machine waits before receiving another part
                    diff = finish_times[conjunctive_parent] - finish_times[current_operation]

                    # if is >0 add it to the time before the beginning of next operation
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

                # print(f"{next.part.get_name()} ({next.item_number})  start: {start}  "
                #       f"duration: {next.operation.get_duration()}"
                #       f"  finish: {finish_times[next]}s", end=" | ")

                start_time = gmtime(start)
                finish_time = gmtime(finish_times[next])
                print(f"{next.part.get_name()} ({next.item_number})  {start_time.tm_hour}:"
                      f"{start_time.tm_min}:{start_time.tm_sec}  ->  {finish_time.tm_hour}:{finish_time.tm_min}:{finish_time.tm_sec} ",
                      end=" | ")

                current_operation = next

            print()

        final_time = max(finish_times.values())
        final_time = gmtime(final_time)
        print(f"Total time: {final_time.tm_hour}:{final_time.tm_min}:{final_time.tm_sec}\n")