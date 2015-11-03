import codecs
from scipy.stats import chi2
import pickle


def load_user_logs(input_file):
    print('Load user logs')
    with codecs.open(input_file, 'r') as fr:
        logs = {}
        for row in fr:
            cols = row.strip().split('\t')

            user = cols[0]
            for i in range(1, len(cols)):
                if 'u_' + user not in logs:
                    logs['u_' + user] = set()

                logs['u_' + user].add('i_' + cols[i])

    return logs



def load_raw_logs(test, input_file, user_index, item_index, rating_index):
    print('Load user logs')
    with codecs.open(input_file, 'r') as fr:
        train = {}
        index = 0
        for row in fr:
            cols = row.strip().split('::')

            index += 1
            if index % 10000 == 0:
                print(index)

            user = 'u_' + cols[user_index]
            item = 'i_' + cols[item_index]
            rating = float(cols[rating_index])
            if  user not in train:
                train[user] = {}
                train[user][item] = rating

            if item not in train[user] and item not in test[user]:
                train[user][item] = rating

    return train


def cal_user_weights(ratings, alpha):
    item_users = {}
    print('Build inverse table for item_users')
    for u, items in ratings.items():
        for i in items.keys():
            if i not in item_users:
                item_users[i] = set()

            item_users[i].add(u)

    print('Calculate co-rated items between users')
    C = {}
    N = {}
    for i, users in item_users.items():
        for u in users:
            for v in users:
                if  u == v:
                    continue

                if u not in C:
                    C[u] = {}
                    C[u][v] = 0
                    N[u] = {}
                    N[u][v] = 0

                if v not in C[u]:
                    C[u][v] = 0
                    N[u][v] = 0

                N[u][v] += 1
                C[u][v] += (ratings[u][i] - ratings[v][i])**2

    print('Calculate final similarity matrix')
    W = {}
    for u, related_users in C.items():
        if u not in W:
            W[u] = {}
        for v, cuv in related_users.items():
            if v not in W[u]:
                W[u][v] = 0
            W[u][v] = cuv / chi2.ppf(alpha / 2, N[u][v])

    return W


def write_matrix(W, filename):
    print('Graph storing')
    with open(filename, 'wb') as fp:
        pickle.dump(W, fp)


if __name__ == '__main__':
    train_data = '../data/MovieLens/ratings.dat'
    test_data = '../data/MovieLens/test.dat'

    # load test data
    test_logs = load_user_logs(test_data)

    # load user logs
    user_rating_info = load_raw_logs(test_logs, train_data, 0, 1, 2)

    # user to user weight calculation
    user_matrix = cal_user_weights(user_rating_info, 0.05)

    write_matrix(user_matrix, 'MovieLens.matrix')
