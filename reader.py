import re
from model import Machine, Part


class Reader:
    def __init__(self):
        pass

    def read_file(self, path):

        file_sections = ["Available machines", "Machine features", "Part list", "Part operations"]

        machines = []
        parts = []
        number = {
            "no limit": float("inf"),
            "one": 1,
            "two": 2
        }

        with open(path) as file:

            lines = list(filter(lambda x: x != "" and "#" not in x, [line.strip() for line in file]))
            i = 1
            while not self.match_strings(lines[i], file_sections[1]):
                machines.append(Machine(lines[i].split(" ", 1)[1]))
                i += 1

            i += 1
            for machine in machines:
                capacity = re.sub("(\s.+){4}$", "", re.sub("^.*:.*:\s", '', lines[i]))
                cooldown = re.sub("^.*:\s", '', lines[i + 1])

                if cooldown.lower() == "none":
                    cooldown = 0
                else:
                    cooldown = int(re.findall("[0-9]+", cooldown)[0])

                machine.set_capacity(number[capacity])
                machine.set_cooldown(cooldown)
                i += 2

            i += 1
            while not self.match_strings(lines[i], file_sections[3]):
                part_name = re.sub("\s-.*$", "", re.sub("^.{3}", "", lines[i]))
                no_items = re.findall("[0-9]+", re.findall("-.*$", lines[i])[0])[0]

                part = Part(part_name)
                part.set_no_items(int(no_items))
                parts.append(part)
                i += 1

            index = -1

            i += 1
            while i < len(lines):

                if re.findall("^[0-9]+:", lines[i]):
                    index += 1
                    part = parts[index]

                machine = re.sub(":.*$", "", re.sub("^.*-\s", "", lines[i]))
                seconds = re.findall("[0-9]+", re.findall(":\s[0-9]+.*$", lines[i])[0])[0]

                for m in machines:
                    if self.match_strings(machine, m.get_name()):
                        machine = m
                        break
                part.add_operation(machine, int(seconds))
                i += 1

        return machines, parts

    @staticmethod
    def match_strings(string1, string2):
        """
        Check if two string partially match based on a percentage.
        :param string1: string
        :param string2: string
        :return: boolean
        """
        string1 = string1.lower().replace(" ", "")
        string2 = string2.lower().replace(" ", "")
        i = 0
        j = 0
        match = 0
        len_s1 = len(string1)
        len_s2 = len(string2)

        while i < len_s1 and j < len_s2:

            if string1[i] == string2[j]:
                match += 1
            else:
                match -= 1
                if j < len_s2 - 1 and string1[i] == string2[j+1]:
                    j += 1
                elif i < len_s1 - 1 and string1[i+1] == string2[j]:
                    i += 1

            i += 1
            j += 1

        if match < 0 or match * 100 / min(len_s1, len_s2) < 70:
            return False
        return True





