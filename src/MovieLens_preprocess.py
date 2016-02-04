import codecs
from sklearn.cross_validation import train_test_split
import operator
import random
import math


def load_raw_logs(input_file, user_index, movie_index, rating_index):
    print('Load raw logs')
    with codecs.open(input_file, 'r') as fr:
        item_logs = {}
        movie_fans = {}
        for row in fr:
            cols = row.strip().split('::')

            user = cols[user_index]
            item = cols[movie_index]
            rating = int(cols[rating_index])
            if 'i_' + item not in item_logs:
                item_logs['i_' + item] = {}
                movie_fans['i_' + item] = set()

            item_logs['i_' + item]['u_' + user] = rating
            if rating == 5:
                movie_fans['i_' + item].add('u_' + user)

    return item_logs, movie_fans


def load_user_logs(input_file, user_index, movie_index, rating_index):
    print('Load user logs')
    with codecs.open(input_file, 'r') as fr:
        logs = {}
        for row in fr:
            cols = row.strip().split('::')

            user = cols[user_index]
            item = cols[movie_index]
            rating = int(cols[rating_index])
            if user not in logs:
                logs[user] = []

            logs[user].append(item)

    return logs


def split_train_test(item_logs, output_train, output_test):
    print('Split train test')
    train_data = {}
    test_data = {}
    user_train = set()
    for item in item_logs:
        user_list = list(item_logs[item].keys())
        training_index, testing_index = train_test_split(range(len(user_list)), test_size=0.3, random_state=7)

        train_data[item] = [user_list[t] for t in training_index]
        test_data[item] = [user_list[t] for t in testing_index]


    fw_train = codecs.open(output_train, 'w')
    fw_test = codecs.open(output_test, 'w')

    for item in train_data:
        for user in train_data[item]:
            user_train.add(user)
            fw_train.write(user + '\t' + item + '\t' + str(item_logs[item][user]) + '\n')

    for item in test_data:
        for user in test_data[item]:
            if user in user_train:
                fw_test.write(user + '\t' + item + '\t' + str(item_logs[item][user]) + '\n')

    fw_test.close()
    fw_train.close()


def choose_long_tail_items(item_actives):
    user_rating_sum = {}
    total_ratings = 0
    for item, user_ratings in item_actives.items():
        user_rating_sum[item] = sum(user_ratings.values())
        total_ratings += sum(user_ratings.values())

    sorted_items = sorted(user_rating_sum.items(), key = operator.itemgetter(1))
    #print(sorted_items[int(len(sorted_items) * 0.9)][0], sorted_items[int(len(sorted_items) * 0.9)][1], len(sorted_items)-1)
    total_count_20 = int(0.2 * total_ratings)
    candidate_items = []
    for i in range(len(sorted_items)):
        if total_count_20 > 0:
            assert sorted_items[i][1] <= sorted_items[i + 1][1], "Sorting Error"
            candidate_items.append(sorted_items[i][0])
            total_count_20 -= sorted_items[i][1]
        else:
            print(sorted_items[i][1], i)
            break

    #chosen_items = [ candidate_items[i] for i in sorted(random.sample(range(len(candidate_items)), 1000)) ]
    ''' generate the list of niche items
    with codecs.open('../data/MovieLens/niche_item.txt', 'w') as fw:
        for item in candidate_items:
            fw.write(item + '\n')
    '''

    return candidate_items


def choose_test_users(fans, items):
    test = {}
    for i in random.sample(range(len(items)), len(items)):
        if items[i] in fans:
            for user in fans[items[i]]:
                if user not in test:
                    test[user] = items[i]
                    break
    return test


def test_logs_gen(test_set, user_logs, item_set, out_file):
    with codecs.open(out_file, 'w') as fw:
        for user in test_set:
            output_set = []
            output_set.append(test_set[user])
            random_items = []
            for item in item_set:
                if item not in user_logs[user]:
                    random_items.append(item)

            for i in random.sample(range(len(random_items)), 1000):
                assert (random_items[i] not in output_set), "Duplicate items"
                output_set.append(random_items[i])

            assert (test_set[user] == output_set[0])
            fw.write(user + '\t' + ('\t').join(output_set) + '\n')


def train_logs_gen(test_set, user_logs, out_file):
    with codecs.open(out_file, 'w') as fw:
        for user in user_logs:
            output_set = user_logs[user]
            # eliminate  test set from user logs
            if user in test_set:
                output_set.remove(test_set[user])

            # output to train data
            for item in output_set:
                fw.write(user + '\t' + item + '\n')


def H(data):
    if not data:
        return 0
    entropy = 0
    count = {}
    for d in data:
        if d not in count:
            count[d] = 0
        count[d] += 1

    for d in count:
        p_x = float(count[d]/len(data))
        if p_x > 0:
            entropy += - p_x*math.log(p_x, 2)
    return entropy


def user_entropy(infile):
    logs = load_user_logs(infile, 0, 1, 2)
    with codecs.open('../data/MovieLens/user_entropy.txt', 'w') as fw:
        for user in logs:
            ratings = list(logs[user].values())
            entropy = H(ratings)
            fw.write(user + '\t' + str(entropy) + '\n')


def gen_exp_data_precision(in_file, train, test):
    item_activity_all, candidate_users = load_raw_logs(in_file, 0, 1, 2)
    split_train_test(item_activity_all, train, test)


def gen_exp_data_recall(in_file, train, test):
    #TODO need to modify before using the function. Pay attention to load_user_logs
    item_activity_all, candidate_users = load_raw_logs(in_file, 0, 1, 2)
    print(len(item_activity_all))
    long_tail_items = choose_long_tail_items(item_activity_all)
    print(len(long_tail_items))

    test_users = choose_test_users(candidate_users, long_tail_items)
    user_activity_all = load_user_logs(in_file, 0, 1)
    print(len(test_users))

    test_logs_gen(test_users, user_activity_all, item_activity_all.keys(), test)
    train_logs_gen(test_users, user_activity_all, train)


def gen_test_top_5(test_file, out_file):
    test_log = load_user_logs(test_file, 0, 1, 2)
    fw = codecs.open(out_file, 'w')
    for user, logs in test_log.items():
        sorted_logs = sorted(logs.items(), key=operator.itemgetter(1), reverse=True)
        fw.write(user)
        for i in range(len(sorted_logs)):
            fw.write('\t' + sorted_logs[i][0] + ':' + str(sorted_logs[i][1]))
        fw.write('\n')
    fw.close()

def load_movie_cat():
    movie_cats = {}
    cats = set()
    fr = open('../data/MovieLens/m.dat', 'r')
    for row in fr:
        cols = row.strip().split('::')
        movie_cats[cols[0]] = []
        for cat in cols[2].split('|'):
            movie_cats[cols[0]].append(cat)
            cats.add(cat)
    fr.close()
    return movie_cats, cats

def gen_user_preference(logs):
    preference = {}
    movie_cats, cats = load_movie_cat()
    for u in logs:
        preference[u] = {}
        for m in logs[u]:
            for c in movie_cats[m]:
                if c not in preference[u]:
                    preference[u][c] = 0
                preference[u][c] += 1
    with codecs.open('tmp_preference.csv', 'w') as fw:
        fw.write('header')
        for c in sorted(cats):
            fw.write(',' + c)
        fw.write('\n')
        for u in preference:
            fw.write(u)
            for c in sorted(cats):
                if c in preference[u]:
                    fw.write(',' + str(preference[u][c]))
                else:
                    fw.write(',' + str(0))
            fw.write('\n')



if __name__ == '__main__':
    input_file = '../data/MovieLens/ratings.dat'
    train_file = '../data/MovieLens/train.dat'
    test_file = '../data/MovieLens/test.dat'


    user_logs = load_user_logs(input_file, 0, 1, 2)
    gen_user_preference(user_logs)
    #item_activity_all, candidate_users = load_raw_logs(input_file, 0, 1, 2)
    #print(len(item_activity_all))

    #gen_exp_data_precision(input_file, train_file, test_file)
    #gen_exp_data_recall(input_file, train_file, test_file)
    #user_entropy(train_file)
    #gen_test_top_5(train_file, 'train_sorted.dat')

    print('Mission Complete')

