import numpy as np
import os


# cuttoff is the precent that is test
def split_file(src, cutoff):
    test_fn = os.path.join('exp_files', os.path.basename(src).split(".")[0] + "_test_%d.txt" % (cutoff*100))
    train_fn = os.path.join('exp_files',
        os.path.basename(src).split(".")[0] + "_train_%d.txt" % ((1-cutoff)*100))

    with open(src, 'rb') as src_file, open(test_fn, 'w') as test_file, \
            open(train_fn, 'w') as train_file:

        for line in src_file:
            r = np.random.uniform()
            if r >= cutoff:
                train_file.writelines(line)
            else:
                test_file.writelines(line)

    return test_fn, train_fn


if __name__ == '__main__':
    split_file("spmf_run3.txt", 0.5)