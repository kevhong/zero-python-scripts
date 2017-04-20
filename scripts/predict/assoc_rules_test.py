import os
import numpy as np
import csv
import pickle

import itertools

import predict_utils

from collections import defaultdict


def train_model(src, minsup, minconf):
    out_fn = os.path.join('exp_files',
                          os.path.basename(src).split(".")[0] + "_assocRules_%d_%d.txt" % (minsup, minconf))
    to_run = 'java -Xmx8192m  -jar spmf.jar run MNR %s %s %d%% %d%%' % \
             (src, out_fn, minsup, minconf)
    print to_run
    os.system(to_run)
    return out_fn


# rules always stored in
def create_dict(rules_file):
    out_fn = os.path.join('exp_files',
                          os.path.basename(rules_file).split(".")[0] + "_pickle.txt")
    rules_dic = defaultdict(list)
    with open(rules_file, 'rb') as rules:
        for row in rules:
            parsed = row.split(" ==>")
            print row
            key = reduce(lambda x, y: "%s %d" % (x, y),
                         sorted(map(lambda x: int(x),
                                    parsed[0].strip().split(" "))),
                         "").strip()
            #print key
            val = reduce(lambda x, y: "%s %d" % (x, y),
                         sorted(map(lambda x: int(x),
                                    parsed[1][0:parsed[1].find("#SUP:")].strip().split(" "))),
                         "").strip()
            #print val
            conf = float(parsed[1].split(" ")[-1])
            #print conf
            rules_dic[key].append((val, conf))

    with open(out_fn, 'wb') as handle:
        pickle.dump(rules_dic, handle)

    return rules_dic


def evaluate(rules_file, test_file, train_amt, rules_dic={},
             dest_file='spmf_run3_results.txt',
             dest_log='spmf_run3_log.txt',
             eval_point=5,
             groupBy=1,
             min_conf=0.35,
             verbose=False):

    r_f = os.path.join('exp_files',
                       os.path.basename(rules_file).split(".")[0] + "_pickle.txt")

    if len(rules_dic) == 0:
        with open(r_f, 'rb') as handle:
            rules_dic = pickle.loads(handle.read())

    # http://stackoverflow.com/questions/952914/making-a-flat-list-out-of-list-of-lists-in-python
    flatten = lambda l: [item for sublist in l for item in sublist]

    temp_file = create_grouping(test_file, groupBy)

    unique_pages = set()

    stats = []

    def get_all_subseq(input_string):
        length = len(input_string)
        return [input_string[i:j + 1] for i in xrange(length) for j in xrange(i, length)]

    with open(temp_file, 'rb') as test:
        next(test)
        for row in test:
            # print row
            vals = map(lambda x: int(x), row.split(" "))
            for v in vals:
                unique_pages.add(v)

            if len(vals) > eval_point:
                know = vals[0:eval_point]
                # print know
                unknown = vals[eval_point:]
                # print unkown

                guesses = set()

                # keys always in increasing order, so we generate all possible
                to_guess = map(lambda g:
                               reduce(lambda x, y: "%s %d" % (x, y), g, "").strip(),
                               get_all_subseq(know))

                for g in to_guess:
                    # print g
                    # print rules_dic[g]
                    to_add = flatten(
                        map(lambda g: map(lambda x: int(x), g),
                            map(lambda x: x[0].split(),
                                filter(lambda x: x[1] >= min_conf, rules_dic[g]))))
                    # print to_add
                    # print set(to_add)
                    for t_a in set(to_add):
                        guesses.add(t_a)

                for x in know:  # don't guess part of what we have already seen
                    guesses.discard(x)

                found = 0
                for p in guesses:
                    if p in unknown:
                        found += 1

                precision = float(found) / len(guesses) if len(guesses) != 0 else 0
                recall = float(found) / len(unknown) if len(unknown) != 0 else 0

                stats.append((found,
                              len(guesses),
                              len(unknown),
                              precision,
                              recall))


    stat_fN = os.path.join("logged",
                      os.path.basename(rules_file).split(".")[0] +
                           '_results_{:d}_{:d}_{:d}.txt'.format(groupBy, eval_point, int(100*min_conf)))


    with open(stat_fN, 'wb') as csvfile:
        s_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for s in stats:
            s_writer.writerow(list(s))

    def aggregate_stats(place):
        count = 0
        for x in stats:
            count += x[place]
        return count

    total_found = aggregate_stats(0)
    total_guesses = aggregate_stats(1)
    total_unknown = aggregate_stats(2)

    def find_avg_and_var(place):
        data = map(lambda x: x[place], stats)
        return float(np.mean(data)),float(np.var(data))

    avg_found, var_found = find_avg_and_var(0)
    avg_guesses, var_guesses = find_avg_and_var(1)
    avg_unknown, var_unknown = find_avg_and_var(2)


    overall_precision = float(total_found) / float(total_guesses) if total_guesses != 0 else 0
    overall_recall = float(total_found) / float(total_unknown) if total_unknown != 0 else 0

    avg_precision, var_precision = find_avg_and_var(3)
    avg_recall, var_recall = find_avg_and_var(4)

    os.system('rm %s' % (temp_file))

    dest = open(dest_file, 'a')
    dest.write("--" * 50 + "\n")
    dest.write('Run Config\n'
               ' Rules File: {}\n'
               ' Test File: {}\n'
               ' Eval_Point: {:d}\n'
               ' Xct in a Group: {:d}\n'
               ' MinCon: {:.2f}\n'
               .format(rules_file,
                       test_file,
                       eval_point,
                       groupBy,
                       min_conf))
    dest.write("Unique pages: %d\n" % (len(unique_pages)))
    dest.write('Run Result\n'
               ' Xct Analyzed: {:d}\n'
               ' Avg Precision: {:.4f}\n'
               ' Var Precision: {:.4f}\n'
               ' Avg Recall: {:.4f}\n'
               ' Var Recall: {:.4f}\n'
               ' Avg Found: {:.4f}\n'
               ' Var Found: {:.4f}\n'
               ' Avg Guesses: {:.4f}\n'
               ' Var Guesses: {:.4f}\n'
               ' Avg Unknown: {:.4f}\n'
               ' Var Unknown: {:.4f}\n'
               ' Overall Precision: {:.4f}\n'
               ' Overall Recall: {:.4f}\n'
               ' Total Found: {:d}\n'
               ' Total Guesses: {:d}\n'
               ' Total Unknown: {:d}\n'
               .format(len(stats),
                       avg_precision,
                       var_precision,
                       avg_recall,
                       var_recall,
                       avg_found,
                       var_found,
                       avg_guesses,
                       var_guesses,
                       avg_unknown,
                       var_unknown,
                       overall_precision,
                       overall_recall,
                       total_found,
                       total_guesses,
                       total_unknown))
    if verbose:
        dest.write(str(stats) + "\n")
    dest.write("--" * 50 + "\n\n")
    dest.close()

    dest = open(dest_log, 'a')
    dest.write('{:d},{:.2f},{:d},{:d},{:d},'.format(train_amt,
                                                    min_conf,
                                                    groupBy,
                                                    eval_point,
                                                    len(unique_pages)))
    dest.write('{:d},'
               '{:.4f},{:.4f},'
               '{:.4f},{:.4f},'
               '{:.4f},{:.4f},'
               '{:.4f},{:.4f},'
               '{:.4f},{:.4f},'
               '{:.4f},{:.4f},'
               '{:d},{:d},{:d}\n'
               .format(len(stats),
                       avg_precision,
                       var_precision,
                       avg_recall,
                       var_recall,
                       avg_found,
                       var_found,
                       avg_guesses,
                       var_guesses,
                       avg_unknown,
                       var_unknown,
                       overall_precision,
                       overall_recall,
                       total_found,
                       total_guesses,
                       total_unknown))
    dest.close()


def create_grouping(src, groupBy=1):
    out_fn = os.path.join('exp_files',
                          os.path.basename(src).split(".")[0] + "_groupedBy_%d.txt" % (groupBy))

    with open(src, 'rb') as src_file, open(out_fn, 'w') as out_file:
        reader = csv.reader(src_file, delimiter=' ', quotechar='|')
        count = 0
        to_write = []
        written = set()
        for row in reader:
            for item in row:
                if item not in written:
                    to_write.append(item)
                    written.add(item)
            count += 1
            if count % groupBy == 0:
                out_file.write(reduce(lambda x, y: str(x) + " " + str(y),
                                      to_write) + '\n')
                to_write = []
                written = set()

    return out_fn


if __name__ == '__main__':
    # test, train = predict_utils.split_file("spmf_run3.txt", 0.5)

    # train_grouped = create_grouping('spmf_run3_train_50.txt', 1)
    # model = train_model('spmf_run3_train_50.txt', 1, 25)
    # rules_dict = create_dict('spmf_run3_train_50_assocRules_15_25.txt')
    #

    # print 'Starting Run on SPMF_run3'
    # for test_part in [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
    #     test, train = predict_utils.split_file("spmf_run3.txt", test_part)
    #     if test_part == 0:
    #         test = train
    #
    #     train_grouped = create_grouping(train, 1)
    #
    #     model = train_model(train_grouped, 20, 30)
    #     rules_dict = create_dict(model)
    #
    #     for g_B in range(1, 6):
    #         for e_points in xrange(3, 8):
    #             for m_conf in [0.1, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95]:
    #                 evaluate(model,
    #                          test, int(100 * (1 - test_part)),
    #                          rules_dic = rules_dict,
    #                          dest_file = 'spmf_run3_full.txt',
    #                          dest_log = 'spmf_run3_log.txt',
    #                          eval_point = e_points,
    #                          groupBy = g_B,
    #                          min_conf = m_conf)
    #                 print 'Done with Group By {:d}, E_p {:d}, m_conf {:.2f}'.format(g_B, e_points, m_conf*100)


    # Server
    print 'Starting Run on SPMF_run3'
    for test_part in [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
        test, train = predict_utils.split_file("spmf_run3.txt", test_part)
        if test_part == 0:
            test = train

        train_grouped = create_grouping(train, 1)

        model = train_model(train_grouped, 5, 9)
        rules_dict = create_dict(model)

        for g_B in range(1, 6):
            for e_points in xrange(3, 8):
                for m_conf in [0.1, 0.15, 0.2, 0.25, 0.35,
                               0.4, 0.45, 0.5, 0.55, 0.60, 0.65, 0.7, 0.75, 0.8, 0.85, 0.95]:
                    evaluate(model,
                             test, int(100 * (1 - test_part)),
                             rules_dic=rules_dict,
                             dest_file='spmf_run3_full.txt',
                             dest_log='spmf_run3_log.txt',
                             eval_point=e_points,
                             groupBy=g_B,
                             min_conf=m_conf)
                    print 'Done with Group By {:d}, E_p {:d}, m_conf {:.2f}'.format(g_B, e_points,
                                                                                    m_conf * 100)

    # evaluate('spmf_run3_train_30_assocRules_20_30.txt',
    #          'spmf_run3_test_70.txt', int(100 * (1 - test_part)),
    #          dest_file='spmf_run3_full.txt',
    #          dest_log='spmf_run3_log.txt',
    #          eval_point=5,
    #          groupBy=1,
    #          min_conf=0.35)
