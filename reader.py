import re
from model import Machine, Part


# def match_strings(string1, string2):
#
#     string1 = string1.lower()
#     string2 = string2.lower()
#     string1_list = string1.split(" ")
#     string2_list = string2.split(" ")
#     match = 0
#     min_length = min(len(string1_list), len(string2_list))
#
#     i = 0
#     j = 0
#     while i < min_length:
#
#         if string1_list[i] in string2:
#             string2 = string2.replace(string1_list[i], "")
#             string1 = string1.replace(string1_list[i], "")
#             match += 1
#
#         if string2_list[j] in string1:
#             string1 = string1.replace(string2_list[j], "")
#             string2 = string2.replace(string2_list[i], "")
#             match += 1
#
#         i += 1
#         j += 1
#
#     if len(string1_list) < len(string2_list):
#         while j < len(string2_list):
#
#             if string2_list[j] in string1:
#                 string1 = string1.replace(string2_list[j], "")
#                 match += 1
#             j += 1
#
#     else:
#         while i < len(string1_list):
#
#             if string1_list[i] in string2:
#                 string2 = string2.replace(string1_list[i], "")
#                 match += 1
#             i += 1
#
#     if match * 100 / min_length >= 80:
#         return True
#     return False


def match_strings(string1, string2):

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


def read_file(path):

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
        while not match_strings(lines[i], file_sections[1]):
            machines.append(Machine(lines[i].split(" ", 1)[1]))
            i += 1

        i += 1
        for machine in machines:
            capacity = re.sub("(\s.+){4}$", "", re.sub("^.*:.*:\s", '', lines[i]))
            cooldown = re.sub("^.*:\s", '', lines[i+1])

            if cooldown.lower() == "none":
                cooldown = 0
            else:
                cooldown = int(re.findall("[0-9]+", cooldown)[0])

            machine.set_capacity(number[capacity])
            machine.set_cooldown(cooldown)
            i += 2

        i += 1
        while not match_strings(lines[i], file_sections[3]):
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
                if match_strings(machine, m.get_name()):
                    machine = m
                    break
            part.add_operation(machine, int(seconds))
            i += 1

    return machines, parts


