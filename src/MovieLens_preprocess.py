import codecs
from sklearn.cross_validation import train_test_split
import operator
import random


def load_raw_logs(input_file, user_index, movie_index, rating_index):
    with codecs.open(input_file, 'r') as fr:
        index = 0
        item_logs = {}
        movie_fans = {}
        for row in fr:
            cols = row.strip().split('::')
            index += 1
            if index % 10000 == 0:
                print(index)

            user = cols[user_index]
            item = cols[movie_index]
            rating = int(cols[rating_index])
            if 'i_' + item not in item_logs:
                item_logs['i_' + item] = set()
                movie_fans['i_' + item] = set()

            item_logs['i_' + item].add('u_' + user)
            if rating == 5:
                movie_fans['i_' + item].add('u_' + user)

    return item_logs, movie_fans


def load_user_logs(input_file, user_index, movie_index):
    with codecs.open(input_file, 'r') as fr:
        index = 0
        logs = {}
        for row in fr:
            cols = row.strip().split('::')
            index += 1
            if index % 10000 == 0:
                print(index)

            user = cols[user_index]
            item = cols[movie_index]
            if 'u_' + user not in logs:
                logs['u_' + user] = set()

            logs['u_' + user].add('i_' + item)


    return logs


def split_train_test(item_logs, output_train, output_test):
    fw_train = codecs.open(output_train, 'w')
    fw_test = codecs.open(output_test, 'w')

    for item in item_logs:
        user_list = list(item_logs[item])
        training_index, testing_index = train_test_split(range(len(item_logs[item])), test_size=0.3, random_state=7)

        for t in training_index:
            fw_train.write('u_' + user_list[t] + '\t' + 'i_' + item + '\n')

        for t in testing_index:
            fw_test.write('u_' + user_list[t] + '\t' + 'i_' + item + '\n')

    fw_test.close()
    fw_train.close()


def choose_long_tail_items(item_actives):
    user_counts = {}
    total_count = 0
    for item in item_actives:
        user_counts[item] = len(item_actives[item])
        total_count += len(item_actives[item])

    sorted_items = sorted(user_counts.items(), key = operator.itemgetter(1), reverse=True)
    #print(sorted_items[int(len(sorted_items) * 0.9)][0], sorted_items[int(len(sorted_items) * 0.9)][1], len(sorted_items)-1)
    indices = [i for i in range(int(len(sorted_items) * 0.2), int(len(sorted_items) * 0.9))]
    total_count_20 = int(0.2 * total_count)
    movie_count = len(sorted_items) - 1
    candidate_items = []
    for i in range(movie_count):
        if total_count_20 > 0:
            candidate_items.append(sorted_items[movie_count - i][0])
            total_count_20 -= sorted_items[movie_count - i][1]
        else:
            print(sorted_items[movie_count - i][1], movie_count - i)
            break

    #chosen_items = [ candidate_items[i] for i in sorted(random.sample(range(len(candidate_items)), 1000)) ]

    return candidate_items


def choose_test_users(fans, items):
    test = {}
    for i in items:
        if i in fans:
            for user in fans[i]:
                if user not in test:
                    test[user] = i
                    break

    return test


def test_logs_gen(test_set, user_logs, item_set, out_file):
    with codecs.open(out_file, 'w') as fw:
        for user in test_set:
            output_set = set()
            output_set.add(test_set[user])
            random_items = []
            for item in item_set:
                if item not in user_logs[user]:
                    random_items.append(item)

            for i in sorted(random.sample(range(len(random_items)), 1000)):
                output_set.add(random_items[i])

            fw.write(user + '\t' + ('\t').join(list(output_set)) + '\n')

if __name__ == '__main__':
    item_activity_all, candidate_users = load_raw_logs('../data/MovieLens/ratings.dat', 0, 1, 2)
    long_tail_items = choose_long_tail_items(item_activity_all)
    test_users = choose_test_users(candidate_users, long_tail_items)
    user_activity_all = load_user_logs('../data/MovieLens/ratings.dat', 0, 1)
    print(len(test_users))

    test_logs_gen(test_users, user_activity_all, item_activity_all.keys(), '../data/MovieLens/test.dat')
    #split_train_test(user_activity_all, '../data/MovieLens/train.dat', '../data/MovieLens/test.dat')

