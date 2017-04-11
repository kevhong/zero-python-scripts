import csv
import sys


def convert(pid_file, output_file):
    with open(pid_file, 'rb') as csvfile, open(output_file, 'w') as outfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            to_write = []
            written = set()
            for item in row[1:]:
               if item not in written:
                   to_write.append(item)
                   written.add(item)

            outfile.write(reduce(lambda x, y: str(x)  + " " + str(y),
                                 to_write) + '\n')


if __name__ == '__main__':
    convert(sys.argv[1], 'spmf.txt')