import csv
import os

from collections import defaultdict


def _write_dict(out, res_fn):
    """
    Helper to write out dictionaries
    :param out: dictionary to write out
    :param res_fn: file name
    :return: void
    """
    output_file1 = open(res_fn + "_multiple.txt", "w")
    output_file2 = open(res_fn + "_all.txt", "w")
    for (k, v) in out.iteritems():
        if len(v) > 1:
            out_string = k + "," + reduce(lambda x, y: x + "," + y, v) + "\n"
            output_file1.write(out_string)
            output_file2.write(out_string)
        else:
            output_file2.write(k + "," + v[0] + "\n")

    output_file1.close()
    output_file2.close()


def _create_pid_files(fn, res_fn):
    """
    Looks at list of transaction request patterns
    and converts them to the form
    pid,xct,xct...
    :param fn: access info file
    :param res_fn: file to write to
    :return: void
     """
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


    _write_dict(out, res_fn)


def _create_xct_files(fn, res_fn):
    """
    Looks at list of transaction request patterns
    and converts them to the form
    xct, pid, pid
    :param fn: access info file
    :param res_fn: file to write to
    :return: void
     """
    out = defaultdict(list)
    with open(fn, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            tid = row[0]
            try:
                pid = row[2]
            except IndexError:
                pid = row[1]


            out[tid].append(pid)

    _write_dict(out, res_fn)


# look at restart and tag those pages that need recovery
# find what precent are needed single page recovery


# clean this up as this looks somewhat promising
# make sure not buggy
def find_precent_recovered(sp_file, xct_file):
    recovered = set()
    restart = set()
    with open(sp_file, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            tid = row[0]
            if tid != 'NoTID':
                recovered.add(row[2])
            else:
                restart.add(row[1])

    vals = []
    with open(xct_file, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            rec = 0
            res = 0
            for x in xrange(1, len(row)):
                curr_page = row[x]
                if curr_page in recovered:
                    rec += 1
                elif curr_page in restart:
                    res += 1
            vals.append((len(row) - 1, rec, res))

    out_test = open('test.txt', 'w+')
    for v in vals:
        out_test.write(reduce(lambda x, y: str(x) + "," + str(y), v) + "\n")
    out_test.close()

    # find some type of window for when it was recovered (Find some precent)


#TODO same page accessed over and over again

if __name__ == '__main__':
    # access_info_l = os.path.join('test_data', 'load', 'page_fix_pid_info.txt')
    # pid_res_fn_l = os.path.join('outputs', 'load', 'pid_to_xct')
    # xct_res_fn_l = os.path.join('outputs', 'load', 'xct_to_pid')
    #
    # _create_pid_files(access_info_l, pid_res_fn_l)
    # _create_xct_files(access_info_l, xct_res_fn_l)
    #
    # access_info_r = os.path.join('test_data', 'restart', 'page_fix_pid_info.txt')
    # pid_res_fn_r = os.path.join('outputs', 'restart', 'pid_to_xct')
    # xct_res_fn_r = os.path.join('outputs', 'restart', 'xct_to_pid')
    #
    # _create_pid_files(access_info_r, pid_res_fn_r)
    # _create_xct_files(access_info_r, xct_res_fn_r)

    find_precent_recovered(os.path.join('test_data', 'restart', 'single_page_recovery_info.txt'),
                           os.path.join('outputs', 'restart', 'xct_to_pid_multiple.txt'))
