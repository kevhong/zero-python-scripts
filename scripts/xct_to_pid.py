import sys
import csv

from collections import defaultdict


'''
Looks at list of transaction request patterns and converts them
to the form
pid,xct,xct
'''

def _convert_file (fn):
    out = defaultdict(list)
    with open(fn, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            tid = row[0]

            try:
                pid = row[2]
            except IndexError:
                pid = row[1]

            out[pid].append(tid)

    new_file = "TODO_pid_file.txt"
    output_file = open(new_file, "w")
    for (k, v) in out.iteritems():
        if (len(v) > 1):
            out_string = k + "," + reduce(lambda x, y: x + "," + y, v)  + "\n"
            output_file.write(out_string)
    output_file.close()


if __name__ == '__main__':
    _convert_file(sys.argv[1])
