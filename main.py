import csv
import numpy
from apriori import Apriori
from fpgrowth import FPGrwoth
from dummy import Dummy
import objgraph
import os
import datetime
from collections import Counter
import linecache
import tracemalloc

def display_top(snapshot, key_type='lineno', limit=3):
    snapshot = snapshot.filter_traces((
        tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
        tracemalloc.Filter(False, "<unknown>"),
    ))
    top_stats = snapshot.statistics(key_type)

    print("Top %s lines" % limit)
    for index, stat in enumerate(top_stats[:limit], 1):
        frame = stat.traceback[0]
        # replace "/path/to/module/file.py" with "module/file.py"
        filename = os.sep.join(frame.filename.split(os.sep)[-2:])
        print("#%s: %s:%s: %.1f KiB"
              % (index, filename, frame.lineno, stat.size / 1024))
        line = linecache.getline(frame.filename, frame.lineno).strip()
        if line:
            print('    %s' % line)

    other = top_stats[limit:]
    if other:
        size = sum(stat.size for stat in other)
        print("%s other: %.1f KiB" % (len(other), size / 1024))
    total = sum(stat.size for stat in top_stats)
    print("Total allocated size: %.1f KiB" % (total / 1024))


# grocery
filename = './dataset/GroceryStore/Groceries.csv'
with open(filename, encoding='utf-8') as f:
    reader = list(csv.reader(f))
del reader[0]
D = list()
for i in reader:
    items = i[1][1:-1].split(',')
    D.append(list(set(items)))

# D = list()
# for i in range(8, 9):
#     f = open('./dataset/UNIX_usage/USER' + str(i) + '/sanitized_all.981115184025', 'r', encoding='utf8')
#     lines = f.readlines()
#     transaction = list()
#     for line in lines:
#         if line[:-1] == '**EOF**':
#             if len(transaction) > 0:
#                 D.append(list(set(transaction)))
#                 transaction = list()
#             continue
#
#         if line[0] == '-' or line[0] == '<' or line[0] == '>' or line[0] == '|' or line[0] == '&' or line[0] == '\n' or line[:-1] =='**SOF**':
#             continue
#         transaction.append(line[:-1])

# objgraph.show_growth()
# D = [
#     ['I1', 'I2', 'I5'],
#     ['I2', 'I4'],
#     ['I2', 'I3'],
#     ['I1', 'I2', 'I4'],
#     ['I1', 'I3'],
#     ['I2', 'I3'],
#     ['I2', 'I3'],
#     ['I2', 'I3'],
#     ['I1', 'I3'],
#     ['I1', 'I2', 'I3', 'I5'],
#     ['I1', 'I2', 'I3', 'I4', 'I5'],
#     ['I1', 'I2', 'I3', 'I4', 'I5'],
#     ['I1', 'I2', 'I3'],
#     ['I1']
# ]
# objgraph.show_growth()
# tracemalloc.start()
# starttime = datetime.datetime.now()

min_sup = 0.005
min_conf = 0.001
# a = Apriori(min_sup, min_conf, D)
f = FPGrwoth(min_sup, min_conf, D)
# d = Dummy(min_sup, min_conf, D)
# item1 = a.apriori()
item2 = f.fp_growth()
# item3 = d.dummy()
# print(item1)
item2 = list(item2)
item2 = sorted(item2, key=lambda item : item[1], reverse=True)
for i in range(0, 20):
    print('Items: ' + str(item2[i][0]) + ' Support: ' + str(item2[i][1]))
# print(item3)
# print(a.generate_rules())
rules = f.generate_rules()
rules = sorted(rules, key=lambda item : item[1], reverse=True)
for i in range(0, 20):
    print('Items: ' + str(rules[i][0]) + ' Confidence: ' + str(rules[i][1]) + ' Kulc: ' + str(rules[i][2]) + ' IR: ' + str(rules[i][3]) )
print()
rules = sorted(rules, key=lambda item : item[2], reverse=True)
for i in range(0, 20):
    print('Items: ' + str(rules[i][0]) + ' Confidence: ' + str(rules[i][1]) + ' Kulc: ' + str(rules[i][2]) + ' IR: ' + str(rules[i][3]) )



# print(d.generate_rules())
# endtime = datetime.datetime.now()
# print((endtime - starttime).microseconds)
# objgraph.show_growth()
# snapshot = tracemalloc.take_snapshot()
# display_top(snapshot)