import re
from copy import deepcopy


def _ext(address):
    with open(address, 'r', encoding="utf-8") as f:
        f_list = f.readlines()
        if len(f_list) > 12:
            name = f_list[8].split('\"')[1]
            structure = {}
            f_dict = []
            f_dict_object = {}
            for i in range(13, len(f_list)):
                match_obj = re.match(r'\t\t\t\[[0-9]*\]', f_list[i])
                if match_obj:
                    f_dict.append(deepcopy(f_dict_object))
                    f_dict_object.clear()
                else:
                    indent = f_list[i].count('\t')
                    if indent == 4:
                        if not re.search(r'vector', f_list[i]):
                            line = f_list[i].split('=', 1)
                            line_1 = line[0].split(' ')
                            length = len(line_1)
                            key = line_1[length - 2]
                            value = line[1].replace('\"', '').replace('\n', '').replace(' ', '').replace('\\n',
                                                                                                         '')
                            value_len = len(value)
                            value_type = line_1[length - 3].replace('\t', '')
                            if structure.__contains__(key):
                                structure[key][1] = max(structure[key][1], value_len)
                            else:
                                structure[key] = [value_type, value_len]
                            f_dict_object[key] = value
            f_dict.append(f_dict_object)
        f.close()
    return [name, structure, f_dict]
