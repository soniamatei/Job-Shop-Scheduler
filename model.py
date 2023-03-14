class Machine:

    def __init__(self, name):
        self.name = name
        self.cooldown = None
        self.capacity = None

    def set_cooldown(self, cooldown):
        self.cooldown = cooldown

    def set_capacity(self, capacity):
        self.capacity = capacity

    def get_name(self):
        return self.name

    def get_cooldown(self):
        return self.cooldown

    def get_capacity(self):
        return self.capacity

    def __str__(self):
        return self.name + "\n" + \
            " Capacity: " + str(self.capacity) + "\n" + \
            " Cooldown: " + str(self.cooldown) + "\n"


class Operation:

    def __init__(self, machine, duration):
        self.machine = machine
        self.duration = duration

    def get_machine(self):
        return self.machine

    def get_duration(self):
        return self.duration


class Part:

    def __init__(self, name):
        self.name = name
        self.no_items = None
        self.operations = []

    def set_no_items(self, no_items):
        self.no_items = no_items

    def add_operation(self, machine, time):
        self.operations.append(Operation(machine, time))

    def __str__(self):
        s = self.name + "  (" + str(self.no_items) + " items)" + "\n"
        for op in self.operations:
            s += " " + op.get_machine().get_name() + ": " + str(op.get_duration()) + "s" + "\n"
        return s

    def get_name(self):
        return self.name

    def get_operations(self):
        return self.operations

    def get_no_items(self):
        return self.no_items