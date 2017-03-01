import os
import csv
from pymining import itemmining, assocrules, perftesting



page_id_info_all = os.path.join('outputs', 'restart', 'xct_to_pid_multiple.txt')

xct_id_info_all = os.path.join('outputs', 'restart', 'xct_to_pid_multiple.txt')

def _load_page_id_set(pid_file):
    patterns = []
    with open(pid_file, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            patterns.append(set(row[1:]))
    patterns = filter(lambda x: len(x) != 1, patterns)
    return patterns


def frequent_item_set(patterns):
    relim_input = itemmining.get_relim_input(patterns)
    report = itemmining.relim(relim_input, min_support=2)
    out = open('frequent_subset.txt', 'w+')
    for (r, v) in report.iteritems():
        if len(r) > 1:
            out.write(str(r) + ":" + str(v) +  "\n")
    out.close()

def association_item_set(patterns):
    relim_input = itemmining.get_relim_input(patterns)
    item_sets = itemmining.relim(relim_input, min_support=2)
    rules = assocrules.mine_assoc_rules(item_sets, min_support=2, min_confidence=0.5)
    out = open('association_subset.txt', 'w+')
    for r in rules:
        out.write(str(r) + "\n")
    out.close()

if __name__ == '__main__':
    frequent_item_set(_load_page_id_set(page_id_info_all))
    association_item_set(_load_page_id_set(page_id_info_all))
    print len(_load_page_id_set(page_id_info_all))