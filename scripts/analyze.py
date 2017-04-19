import csv
import os


def _move_in_data():
    pass

def _create_restart_info():
    pass

# clean this up as this looks somewhat promising
# make sure not buggy
def find_percent_recovered(sp_file, xct_file):
    recovered = set()
    recovered_by = {}
    restart = set()
    with open(sp_file, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            tid = row[0]
            if tid != 'NoTID':
                recovered.add(row[2])
                if row[2] in recovered_by:
                    print "bug here !!"
                else:
                    recovered_by[row[2]] = tid
            elif tid == 'NoTID':
                restart.add(row[1])

    vals = []
    with open(xct_file, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            rec = 0
            self_rec = 0
            res = 0
            found = set()
            total = 0
            for x in xrange(1, len(row)):
                curr_page = row[x]
                if curr_page not in found:
                    if curr_page in recovered:
                        rec += 1
                        if recovered_by[curr_page] == row[0]:
                            self_rec += 1
                    elif curr_page in restart:
                        res += 1
                    found.add(curr_page)
                    total += 1
            if row[0] != 'NoTID':
                vals.append((row[0], total, rec, self_rec, res))

    out_test = open('percent_recovered.txt', 'w+')
    out_test.write(
        reduce(lambda x, y: str(x) + ", " +  str(y),
               ["TID", "Total Unique Pages Used",
                "SPR Recovered Pages Used",
                "Times Used SPR",
                "Restart Pages Used"]) + "\n")
    vals.sort(key=lambda x: float(x[0]))
    vals.insert(0, ('NoTID', len(restart)))
    for v in vals:
        out_test.write(reduce(lambda x, y: str(x) + "," + str(y), v) + "\n")
    out_test.close()


    # find some type of window for when it was recovered (Find some percent)

if __name__ == '__main__':
    find_percent_recovered(os.path.join('test_data', 'restart', 'single_page_recovery_info.txt'),
                           os.path.join('test_data', 'restart', 'xct_page_usage_info.txt'))