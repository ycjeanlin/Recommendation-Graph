import codecs
import math
import pickle
import time


def load_raw_logs(input_file, user_index, POI_index):
    with codecs.open(input_file, 'r') as fr:
        train = {}
        index = 0
        for row in fr:
            cols = row.strip().split('\t')
            index += 1
            if index % 10000 == 0:
                print(index)
            user = cols[user_index]
            item = cols[POI_index]
            if  user not in train:
                train[user] = {}
                train[user][item] = 1

            if item not in train[user]:
                train[user][item] = 1

    return train


def user_similarity(train):
    item_users = {}
    print('Build inverse table for item_users')
    for u, items in train.items():
        for i in items.keys():
            if i not in item_users:
                item_users[i] = set()

            item_users[i].add(u)

    print('Calculate co-rated items between users')
    C = {}
    N = {}
    for i, users in item_users.items():
        for u in users:
            if u not in N:
                N[u] = 0
            N[u] += 1
            for v in users:
                if  u == v:
                    continue

                if u not in C:
                    C[u] = {}
                    C[u][v] = 0

                if v not in C[u]:
                    C[u][v] = 0

                C[u][v] += 1

    print('Calculate final similarity matrix')
    W = {}
    for u, related_users in C.items():
        if u not in W:
            W[u] = {}
        for v, cuv in related_users.items():
            if v not in W[u]:
                W[u][v] = 0
            W[u][v] = cuv/math.sqrt(N[u] * N[v])

    return W


def write_matrix(W, filename):
    print('Graph storing')
    with open(filename, 'wb') as fp:
        pickle.dump(W, fp)


if __name__ == '__main__':
    train_file = '../data/MovieLens/train.dat'

    user_logs = load_raw_logs(train_file, 0, 1)
    start_time = time.time()
    similarity = user_similarity(user_logs)
    end_time = time.time()
    write_matrix(similarity, 'MovieLens.matrix')
    print("--- %s seconds ---" % (end_time - start_time))