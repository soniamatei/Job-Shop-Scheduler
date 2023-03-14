

class Vertex:

    def __init__(self, part=None, operation=None, start_time=None, item_number=None):
        self.operation = operation
        self.start = start_time
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
        self.edges = []
        self.start = Vertex()
        self.finish = Vertex()

    def create_conjunctive_arcs(self):

        for part in self.parts:
            # introduce as many 'rows' in the graph as many items of one part are there
            for item_number in range(part.get_no_items()):
                operations = part.get_operations()

                prev = self.start
                # a variable which sums up the duration of each operation
                # -> this will determine the starting time of each operation
                accumulated_time = 0
                for op in operations:
                    current = Vertex(part, op, accumulated_time, item_number)

                    self.vertices.append(current)
                    self.edges.append((prev, current))

                    accumulated_time += op.get_duration()
                    prev = current

                self.edges.append((prev, self.finish))

        # for v in self.vertices:
        #     print(v)

    def create_disjunctive_arcs(self):

        for machine in self.machines:
            vertices_by_machine = []

            # get all operations on a specific machine in one list
            for vertex in self.vertices:
                if vertex.operation.get_machine() == machine:
                    vertices_by_machine.append(vertex)

            # make the specific connections between them as follows:
            # t = starting time of the op
            # p = processing time of the op
            # c = cooldown time of the machine
            # t_i + p_i + c <= t_(i+1) + p_(i+1) + c or t_(i+1) + p_(i+1) + c <=  t_i + p_i + c
            for index1 in range(len(vertices_by_machine)):
                for index2 in range(index1 + 1, len(vertices_by_machine)):

                    vertex1 = vertices_by_machine[index1]
                    vertex2 = vertices_by_machine[index2]

                    if vertex1 != vertex2:

                        if vertex1.start + vertex1.operation.get_duration() + machine.get_cooldown() <= \
                                vertex2.start + vertex2.operation.get_duration() + machine.get_cooldown():
                            self.edges.append((vertex1, vertex2))

                        elif vertex2.start + vertex2.operation.get_duration() + machine.get_cooldown() <= \
                                vertex1.start + vertex1.operation.get_duration() + machine.get_cooldown():
                            self.edges.append((vertex2, vertex1))

        # for e in self.edges:
        #     print(e[0], "|", e[1])

    def calculate_length(self, path):
        """
        Calculates the length (duration of operation + machine cooldown) of a path given.
        :param path: list with vertices
        :return: integer
        """
        length = 0
        for vertex in path:
            if vertex.part is not None:
                length += vertex.operation.get_duration() + vertex.operation.get_machine().get_cooldown()

        return length

    def find_path(self, source):
        """
        Algorithm for finding the longest path in a directed graph. A DFS based algorithm which selects
        the longest path found from the adjacent nodes of the source.

        :param source: vertex
        :return: list of vertices
        """

        longest_path = []
        adjacent_nodes = list(filter(lambda x: (source, x) in self.edges, self.vertices))

        for next in adjacent_nodes:
            new_path = self.find_path(next)

            if new_path:
                # if we find a new path
                if not longest_path or self.calculate_length(new_path) > self.calculate_length(longest_path):
                    longest_path = new_path

        longest_path.insert(0, source)
        return longest_path

    def get_overall_time(self):
        """
        Returns the total time of execution of all operations.
        :return: integer
        """
        return self.calculate_length(self.find_path(self.start))

# TODO: machine schedule (first vertex without indegree)