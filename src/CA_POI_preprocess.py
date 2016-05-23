import codecs
import collections
from datetime import datetime as dt

# 2013-07-21 17:25:09 2009-12-07 17:21:43 1322
def conv_raw_to_session(input_file, train_file, test_file):
    threshold_date = dt.strptime('4 20 20:15:24 +0000 2011', '%m %d %H:%M:%S +0000 %Y')
    #min_date = dt.strptime('Dec 30 20:15:24 +0000 2016', '%b %d %H:%M:%S +0000 %Y')
    with codecs.open(input_file, 'r') as fr:
        index_train = 0
        index_test = 0
        fw_train = codecs.open(train_file, 'w')
        fw_test = codecs.open(test_file, 'w')
        index = 0
        for row in fr:
            index += 1
            if index == 1:
                continue

            cols = row.strip().split('\t')
            current_date =  dt.strptime(cols[1], '%a %b %d %H:%M:%S +0000 %Y')

            if threshold_date > current_date:
                fw_train.write(cols[0]+'_'+str(current_date.date()) + ',' + cols[2] + '\n')
                index_train += 1
            else:
                fw_test.write(cols[0]+'_'+str(current_date.date()) + ',' + cols[2] + '\n')
                index_test += 1

        fw_test.close()
        fw_train.close()
    print(index_train, index_test)


def load_conv_logs(input_file, session_index, item_index):
    # Note: the input file must be converted to session, item format
    logs = {}
    index = 0
    with codecs.open(input_file, 'r') as fr:
        for row in fr:
            index += 1
            if (index % 1000) == 0:
                print(index)

            cols = row.strip().split(',')

            session = cols[session_index]
            item = cols[item_index]
            if session not in logs:
                logs[session] = []

            logs[session].append(item)

    return logs


def count_num_feature(input_raw_file, col_index, seperator):
    feature_set = set()
    with codecs.open(input_raw_file, 'r') as fr:
        for row in fr:
            cols = row.strip().split(seperator)
            feature_set.add(cols[col_index])

        print('Number = ', len(feature_set))

def count_activities_session(logs, output_file):
    with codecs.open(output_file, 'w') as fw:
        for s in logs:
            fw.write(str(len(logs[s])) + '\n')

def main():
    raw_file = '../data/CA_foursquare/checkin_CA_venues.txt'
    train_file = '../data/CA_foursquare/conv_train.dat'
    test_file = '../data/CA_foursquare/conv_test.dat'

    #conv_raw_to_session(raw_file, train_file, test_file)
    count_num_feature(train_file, 0, ',')
    #train_logs = load_conv_logs(train_file, 0, 1)
    #count_activities_session(train_logs, 'tmp_exp.csv')

if __name__ == '__main__':
    main()

