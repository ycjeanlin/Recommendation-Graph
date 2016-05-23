import codecs
from datetime import datetime as dt
from random import sample


def load_raw_logs(infile, user_index, date_index, item_index):
    user_log = {}
    with codecs.open(infile, 'r') as fr:
        for row in fr:
            cols = row.strip().split('\t')
            user_id = cols[user_index]
            act_time = dt.strptime(cols[date_index], '%a %b %d %H:%M:%S +0000 %Y')
            item_id = cols[item_index]
            session_id = user_id + '_' + act_time.strftime('%Y-%m-%d')

            if session_id not in user_log:
                user_log[session_id] = []

            user_log[session_id].append(item_id)


def train_test_split(user_log, train_file, test_file):
    fw_train = codecs.open(train_file, 'w')
    fw_test = codecs.open(test_file, 'w')
    for u, log in user_log.items():
        if len(log) > 3:
            test_indices = sample(range(len(log)), 1)
            fw_test(u + '\t' + log[test_indices[0]] + '\n')
            for i in log:
                if i != log[test_indices[0]]:
                    fw_train.write()



if __name__ == '__main__':
    raw_file = '../data/CA_foursquare/checkin_CA_venues.txt'


