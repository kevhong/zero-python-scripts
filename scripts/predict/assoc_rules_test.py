import os
import numpy as np
import csv
import pickle

import predict_utils

from collections import defaultdict




def train_model(src, minsup, minconf):
    out_fn = os.path.basename(src).split(".")[0] + "_assocRules_%d_%d.txt" % (minsup, minconf)
    to_run =  'java -Xmx8192m  -jar spmf.jar run FPGrowth_association_rules %s %s %d%% %d%%' % \
              (src, out_fn, minsup, minconf)
    print to_run
    os.system(to_run)
    return out_fn


def create_dict(rules_file):
    out_fn = os.path.basename(rules_file).split(".")[0] + "_pickle.txt"
    rules_dic = defaultdict(list)
    with open(rules_file, 'rb') as rules:
        for row in rules:
            parsed = row.split("==>")
            try:
                key = int(parsed[0])
                vals = parsed[1][0:parsed[1].find("#SUP:")]
                conf = float(parsed[1].split(" ")[-1])
                temp = map(lambda x: (int(x), conf), vals.split(","))
                rules_dic[key] += temp
            except:
                continue

    with open(out_fn, 'wb') as handle:
        pickle.dump(rules_dic, handle)

    return out_fn, rules_dic


def evaluate(rules_dic, rules_file, test_file,
             dest_file='spm.txt', eval_point=5,
             groupBy=1,
             verbose=False):

    # out_fn = os.path.basename(rules_file).split(".")[0] + "_pickle.txt"
    #
    # rules_dic = {}
    # with open(out_fn, 'rb') as handle:
    #     rules_dic = pickle.loads(handle.read())

    temp_file = create_grouping(test_file, groupBy)

    unique_pages = set()

    stats = []

    with open(temp_file, 'rb') as test:
        next(test)
        for row in test:
            #print row
            vals = map(lambda x : int(x), row.split(" "))
            for v in vals:
                unique_pages.add(v)

            if len(vals) > eval_point:
                know = set(vals[0:eval_point])
                #print know
                to_guess = set(vals[eval_point:])
                #print to_guess


                found = 0
                possible = []
                for x in know:
                    #print rules_dic[x]
                    possible += map(lambda x: x[0], rules_dic[x])

                possible = set(possible)
                #print possible
                for p in possible:
                    if p in to_guess:
                        found += 1
                stats.append((found, len(to_guess),
                             len(possible) - found,
                             float(found)/len(to_guess)))


    t_found = 0
    t_guessed = 0

    for x in stats:
        t_found += x[0]
        t_guessed += x[1]

    mean_right = np.mean(np.array(map(lambda x: x[3], stats)))
    mean_wrong = np.mean(np.array(map(lambda x: x[2]/float(x[1]), stats)))

    os.system('rm %s' % (temp_file))

    dest = open(dest_file, 'a')
    dest.write("--"*50 + "\n")
    dest.write("Run Config\n Rules File: %s\n Test File: %s\n Eval_Point: %d\n Xct in a Group: %d\n"
               % (rules_file, test_file, eval_point, groupBy))
    dest.write("Unique pages: %d\n" % (len(unique_pages)))
    dest.write("Run Result\n "
               "%% Guessed: %.4f\n "
               "Total Guessed: %d\n "
               "Total Unknown: %d\n "
               "Mean %% Guessed: %.4f\n "
                "Mean Number Wrong: %.4f\n "
               % (float(t_found)/ t_guessed,
                  t_found,
                  t_guessed,
                  mean_right,
                  mean_wrong))
    if verbose:
        dest.write(str(stats) + "\n")
    # dest.write("***" * 10 + "\n")
    # dest.write("Rules Dictionary\n")
    # for k, v in rules_dic.iteritems():
    #     dest.write(str(k) + ": " + str(v) + "\n")
    dest.write("--" * 50 + "\n\n")
    dest.close()

def create_grouping(src, groupBy = 1):

    out_fn = os.path.basename(src).split(".")[0] + "_groupedBy_%d.txt" % (groupBy)
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

    model_conf = [(0,0), (20, 35), (30, 45), (37, 53), (45, 60)]

    for y in range(2, 5, 1):
        train_grouped = create_grouping('spmf_run3_train_0.50.txt', y)
        model = train_model(train_grouped, model_conf[y][0], model_conf[y][1])
        p_fn, rules_dict = create_dict(model)
        for x in xrange(1, 10, 2):
            evaluate(rules_dict, model, 'spmf_run3_test_0.50.txt',
                     dest_file='spmf_run3_eval_new.txt',
                     eval_point = 5, groupBy=x)
            print "finished eval for xct group by %d"  % x
        try:
            os.system('rm %s' % (model))
            os.system('rm %s' % (p_fn))
            os.remove('rm %s' % (train_grouped))
        except Exception as inst:
            print inst 
            continue


    for y in range(1, 5, 1):
        if (y - 1) * 20 + 35 > 100:
            break
        train_grouped = create_grouping('spmf_run3_train_0.50.txt', y)
        model = train_model(train_grouped, 20 + (y - 1) * 20, 35 + (y - 1) * 20)
        p_fn, rules_dict = create_dict(model)
        for x in xrange(1, 10, 5):
            evaluate(rules_dict, model, 'spmf_run3_test_0.50.txt',
                     dest_file = 'spmf_run3_eval_verbose_new.txt',
                     eval_point=5, groupBy=x, verbose=True)
            print "finished eval for xct grouped by %d" % x
        try:
            os.system('rm %s' % (model))
            os.system('rm %s' % (p_fn))
            os.remove('rm %s' % (train_grouped))
        except Exception as inst:
            print inst
            continue

    # train_grouped = create_grouping('spmf_run3_train_0.50.txt', 1)
    # model = train_model(train_grouped, 20, 35)
    # p_fn, rules_dict = create_dict(model)
    # evaluate(rules_dict, model, 'spmf_run3_test_0.50.txt',
    #          dest_file='demo.txt',
    #          eval_point=5, groupBy=1)