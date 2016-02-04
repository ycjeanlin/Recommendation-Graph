import codecs
import math
import pickle
import time


def load_raw_logs(input_file, user_index, item_index):
    with codecs.open(input_file, 'r') as fr:
        train = {}
        index = 0
        for row in fr:
            cols = row.strip().split(',')
            index += 1
            if index % 1000000 == 0:
                print(index)
            user = cols[user_index]
            item = cols[item_index]
            if  user not in train:
                train[user] = set()

            train[user].add(item)

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


def item_similarity(user_item):

    print('Calculate co-rated items between users')
    C = {}
    N = {}
    for u, item_set in user_item.items():
        for i in item_set:
            if i not in N:
                N[i] = 0
            N[i] += 1
            for j in item_set:
                if i == j:
                    continue

                if i not in C:
                    C[i] = {}
                    C[i][j] = 0

                if j not in C[i]:
                    C[i][j] = 0

                C[i][j] += 1

    print('Calculate final similarity matrix')
    W = {}
    for i, related_items in C.items():
        if i not in W:
            W[i] = {}
        for j, cij in related_items.items():
            if i == '214851097' and j == '214851234':
                    print('yes')
            W[i][j] = cij/math.sqrt(N[i] * N[j])

    return W


def write_matrix(W, filename):
    print('Graph storing')
    with open(filename, 'wb') as fp:
        pickle.dump(W, fp)


if __name__ == '__main__':
    train_file = '../data/yoochoose/yoochoose-clicks.dat'

    session_logs = load_raw_logs(train_file, 0, 2)
    start_time = time.time()
    similarity = item_similarity(session_logs)
    end_time = time.time()
    write_matrix(similarity, 'yoochoose.matrix')
    print("--- %s seconds ---" % (end_time - start_time))