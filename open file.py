import csv

with open('C:/work/all_data_general_1.csv', 'r') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=';')
    changed_str = ''
    for string in spamreader:
        print(string)
        changed_attr = []
        try:
            group = string[8].split(',')
            # print(group)
            # print('\n')

            for i, attr in enumerate(group):
                count = 0
                param = attr.split(':')
                changed_param = []
                changed = 0
                # print(group)
                for j in range(len(group)):

                    if param[0] == group[j].split(':')[0]:
                        count += 1
                        if count >= 1:
                            status = 1
                            if param[0] != ' ' or param[0] != '':
                                result = param[0] + str(count) + ':' + ':'.join(k for k in param[1:])
                            else:
                                continue

                            try:
                                changed_attr.index(result)
                            except:
                                for b in changed_attr:
                                    if b.split(':')[1:] == param[1:] or b.split(':')[0] == param[0] + str(count):
                                        status = 0
                                if status != 0:
                                    changed_attr.append(result)

            final = []
            for k in changed_attr:
                number = k.split(':')[0]
                if number[-1] == '1':
                    result = number[:-1] + ':' + ':'.join(n for n in k.split(':')[1:])
                else:
                    result = k
                if result != ':':
                    final.append(result)
            # print('result: ', final)
            string.pop(8)

            string.insert(8, ', '.join(v for v in final))
            print(string)
            with open('C:/work/all_data_general_1(edit).csv', 'a', newline='') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(string)
        except BaseException as e:
            print(e)


