import codecs
from scipy.stats import chi2
import pickle


def load_test_logs(input_file, user_index, item_index):
    print('Load test logs')
    with codecs.open(input_file, 'r') as fr:
        logs = {}
        for row in fr:
            cols = row.strip().split('\t')

            user = cols[user_index]
            item = cols[item_index]

            if user not in logs:
                logs[user] = []

            logs[user].append(item)

    return logs



def load_train_logs(input_file, user_index, item_index, rating_index):
    print('Load train logs')
    with codecs.open(input_file, 'r') as fr:
        train = {}
        for row in fr:
            cols = row.strip().split('\t')

            user = cols[user_index]
            item = cols[item_index]
            rating = float(cols[rating_index])
            if  user not in train:
                train[user] = {}

            if item not in train[user]:
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
    index = 0
    for i, users in item_users.items():
        index += 1
        if index % 100 == 0:
            print(index)

        for u in users:
            for v in users:
                if  u == v:
                    continue

                if u not in C:
                    C[u] = {}
                    N[u] = {}

                if v not in C[u]:
                    C[u][v] = 1
                    N[u][v] = 0

                N[u][v] += 1
                C[u][v] += (ratings[u][i] - ratings[v][i])**2

    print('Calculate final similarity matrix')
    W = {}
    speedup = {}
    index = 0
    for u, related_users in C.items():
        index += 1
        if index % 50 == 0:
            print(index)

        if u not in W:
            W[u] = {}
        for v, cuv in related_users.items():
            if N[u][v] not in speedup:
                speedup[N[u][v]] = chi2.ppf(alpha / 2, N[u][v])

            W[u][v] = speedup[N[u][v]] / cuv
            #print(W[u][v], cuv, speedup[N[u][v]])

    return W


def write_matrix(W, filename):
    print('Graph storing')
    with open(filename, 'wb') as fp:
        pickle.dump(W, fp)


if __name__ == '__main__':
    train_data = '../data/MovieLens/train.dat'
    test_data = '../data/MovieLens/test.dat'
    output_matrix = 'MovieLens.matrix'

    # load test data
    test_logs = load_test_logs(test_data, 0, 1)

    # load user logs
    user_rating_info = load_train_logs(train_data, 0, 1, 2)

    # user to user weight calculation
    user_matrix = cal_user_weights(user_rating_info, 0.05)

    write_matrix(user_matrix, 'MovieLens.matrix')
