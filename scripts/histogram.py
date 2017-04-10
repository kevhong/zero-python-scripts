import os
import csv

import numpy as np
import matplotlib.pyplot as plt

'''
Creates Histograms of the recovery times
'''


def _create_single_page_times_hist(fn, get_leaf, res_fn):
    """
    Creates histogram of the recvoery times
    :param fn: single_page_recovery info
    :param get_leaf: do leaf or node
    :param res_fn: resulting file
    :return: void
    """
    times = []
    recovery_times = []
    with open(fn, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            has_children = row[-2] == "1"
            no_tid = row[0] == 'NoTID'
            if not get_leaf:
                if has_children:
                    times.append(row[-1])
                    if no_tid:
                        recovery_times.append(row[-1])
                elif get_leaf and not has_children:
                    times.append(row[-1])
                    if no_tid:
                        recovery_times.append(row[-1])
            elif get_leaf and not has_children:
                times.append(row[-1])
                if no_tid:
                    recovery_times.append(row[-1])

    times = np.asarray(map(lambda x: np.float64(x), times))

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.hist(times, facecolor='green',
            bins=[0, 5, 10, 25, 50, 75, 100,
                  200, 300, 400, 500, 750, 1000])  # add labels?
    plt.xlabel('Buckets of Times (in Microseconds i.e. 10^-6 seconds)')
    plt.ylabel('Count')
    plt.title(('Leaf Page ' if get_leaf else 'Node Page ') +
              ' Single Page Recovery Times')

    total_pages = len(times)
    overall_average = sum(times) / total_pages
    overall_var = np.var(times)

    restart_thread_pages = len(recovery_times)
    recovery_times = map(lambda x: float(x), recovery_times)
    restart_thread_pages_avg = sum(recovery_times) / restart_thread_pages
    restart_thread_pages_var = np.var(times)

    plt.figtext(0.175, 0.7,
                "Total Pages: " + str(total_pages) + "\n" +
                "Total Average: " + str(overall_average) + "\n" +
                "Total Variance: " + str(overall_var) + "\n\n" +
                "NoTID Pages: " + str(restart_thread_pages) + "\n" +
                "NoTID Average: " + str(restart_thread_pages_avg) + "\n" +
                "NoTID Variance: " + str(restart_thread_pages_var),
                fontsize=9)


    plt.savefig("{0}{1}".format(res_fn, ('leaf_single_page_recovery.png'
                                         if get_leaf
                                         else 'node_single_page_recovery.png')))


def _create_xct_access_count_hist(fn, res_fn):
    counts = []
    with open(fn, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            if row[0] == 'NoTid':
                no_tid = len(row) -1
            counts.append(len(set(row)) -1)
            # if len(set(row)) > 10:
            #     print set(row)


    counts = np.asarray(map(lambda x: np.float64(x), counts))

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.hist(counts, facecolor='blue',
            bins=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,
                  13, 14, 15, 20, 30, 40, 50, 100]) # add labels?
    plt.xlabel('Page Access Number Bucket')
    plt.ylabel('Count of Transactions')
    plt.title('Histogram of Xct Page Access Counts')

    more_than_one = len(filter(lambda x: x != 1, counts))

    plt.figtext(0.5, 0.7,
                "Multiple: " + str(more_than_one) +
                "\nSingle: " + str(len(counts) - more_than_one) +
                "\nAverage: " + str(np.mean(counts)) +
                "\nPrecent Multiple: " + str(float(more_than_one) / len(counts)),
                fontsize=12)

    # plt.figtext(0.5, 0.7,
    #             "Recovery Thread: " + str(no_tid),
    #             fontsize=9)

    plt.savefig("{0}{1}".format(res_fn, 'xct_access_hist.png'))



def _create_page_access_count_hist(fn, res_fn):
    counts = []
    with open(fn, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            if row[0] == 'NoTid':
                no_tid = len(row) - 1
            counts.append(len(set(row)) - 1)
            if len(set(row)) > 10:
                pass

    counts = np.asarray(map(lambda x: np.float64(x), counts))

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.hist(counts, facecolor='red',
            bins=[0,1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,
                  13, 14, 15, 20, 30, 40, 50, 100])  # add labels?
    plt.xlabel('Xct Uses Number Bucket')
    plt.ylabel('Count of Pages')
    plt.title('Histogram of Page Usage Counts')

    more_than_one = len(filter (lambda x: x != 1, counts))

    plt.figtext(0.5, 0.7,
                "Multiple: " + str(more_than_one) +
                "\nSingle: " + str(len(counts) - more_than_one) +
                "\nAverage: " + str(np.mean(counts)) +
                "\nPrecent Multiple: " + str(float(more_than_one) / len(counts)),
                fontsize=12)

    plt.savefig("{0}{1}".format(res_fn, 'page_access_hist.png'))


# debug the missing NoTID

if __name__ == '__main__':
    sp_recovery_info = os.path.join('test_data', 'restart',
                                    'single_page_recovery_info.txt')
    sp_recovery_res = os.path.join('outputs', 'restart', '')
    _create_single_page_times_hist(sp_recovery_info, True, sp_recovery_res)
    _create_single_page_times_hist(sp_recovery_info, False, sp_recovery_res)

    xct_info_l = os.path.join('outputs', 'load', 'xct_to_pid_all.txt')
    xct_out_l = os.path.join('outputs', 'load', '')

    _create_xct_access_count_hist(xct_info_l, xct_out_l)

    xct_info_r = os.path.join('outputs', 'restart', 'xct_to_pid_all.txt')
    xct_out_r = os.path.join('outputs', 'restart', '')

    _create_xct_access_count_hist(xct_info_r, xct_out_r)

    pid_info_l = os.path.join('outputs', 'load', 'pid_to_xct_all.txt')
    pid_out_l = os.path.join('outputs', 'load', '')

    _create_page_access_count_hist(pid_info_l, pid_out_l)

    pid_info_r = os.path.join('outputs', 'restart', 'pid_to_xct_all.txt')
    pid_out_r = os.path.join('outputs', 'restart', '')

    _create_page_access_count_hist(pid_info_r, pid_out_r)
