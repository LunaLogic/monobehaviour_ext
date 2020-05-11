import re
from copy import deepcopy


def parse_raw(cursor, db, to_json=0, to_csv=0):
    if to_json:
        shutil.rmtree('output/json', ignore_errors=True)
        os.mkdir('output/json')
    if to_csv:
        shutil.rmtree('output/csv', ignore_errors=True)
        os.mkdir('output/csv')
    type_all = []
    for addr in os.listdir('output/bytes'):
        with open('output/bytes/' + addr, 'r', encoding="utf-8") as f:
            f_lines = f.readlines()
            flag_data = False
            structure = {}
            f_dict = []
            f_dict_object = {}
            flag_end = False
            for line in f_lines:
                if flag_data:
                    if re.match(r'\t\tdata {2}\(' + addr.split('.')[0][:-1] + r'\)', line, re.I):
                        flag_end = False
                        f_dict.append(deepcopy(f_dict_object))
                        f_dict_object.clear()
                    elif line == '\n':
                        if flag_end:
                            break
                        else:
                            flag_end = True
                    else:
                        flag_end = False
                        data_list = line.split(' ')
                        key = data_list[0].replace('\t', '')
                        value = ''
                        value_type = ''
                        if len(data_list) > 3:
                            if '(' not in data_list[2]:
                                value_part = [data_list[1]]
                                for i in range(2, len(data_list) - 1):
                                    value_part.append(data_list[i])
                                    if '"' in data_list[i]:
                                        value_type = data_list[i + 1].replace('\n', '').replace('(', '').replace(')',
                                                                                                                 '')
                                        break
                                value = ''.join(value_part).replace('\"', '').replace('\\n', '')
                            else:
                                value = data_list[1].replace('\"', '').replace('\\n', '')
                                value_type_part = [data_list[2]]
                                for i in range(3, len(data_list)):
                                    value_type_part.append(data_list[i])
                                    if ')' in data_list[i]:
                                        break
                                value_type = ' '.join(value_type_part).replace('\n', '').replace('(', '').replace(')',
                                                                                                                  '')
                        else:
                            value = data_list[1].replace('\"', '').replace('\\n', '')
                            value_type = data_list[2].replace('(', '').replace(')', '').replace('\n', '')
                        value_len = len(value)
                        if not (value_type == 'vector' or data_list[0].count('\t') > 3):
                            type_all.append(value_type)
                            if structure.__contains__(key):
                                structure[key][1] = max(structure[key][1], value_len)
                            else:
                                structure[key] = [value_type, value_len]
                            f_dict_object[key] = value
                else:
                    if re.match(r'\t\tdata {2}\(' + addr.split('.')[0][:-1] + r'\)', line, re.I):
                        flag_data = True
            f_dict.append(f_dict_object)
            if to_json:
                export_json(addr.split('.')[0], f_dict)
            if to_csv:
                export_csv(addr.split('.')[0], f_dict)
            f.close()


def parse_txt(cursor, db, dir_name='MonoBehaviour', to_json=0, to_csv=0):
    for addr in os.listdir(dir_name):
        if os.path.splitext(addr)[1] == '.txt':
            with open(dir_name+'/' + addr, 'r', encoding="utf-8") as f:
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
                                    value = line[1].replace('\"', '').replace('\n', '').replace(' ', '').replace('\\n', '')
                                    value_len = len(value)
                                    value_type = line_1[length - 3].replace('\t', '')
                                    if structure.__contains__(key):
                                        structure[key][1] = max(structure[key][1], value_len)
                                    else:
                                        structure[key] = [value_type, value_len]
                                    f_dict_object[key] = value
                    f_dict.append(f_dict_object)
                    if to_json:
                        export_json(name, f_dict)
                    if to_csv:
                        export_csv(name, f_dict)
                f.close()
    shutil.rmtree(dir_name)

# 导出json格式的原始数据
def export_json(name, f_dict):
    with open('./output/json/' + name + '.json', 'w') as out:
        out.write(json.dumps(f_dict))
        out.close()


# 导出csv格式的原始数据
def export_csv(name, f_dict):
    pandas.DataFrame(f_dict).to_csv('./output/csv/' + name + '.csv', index=False)

