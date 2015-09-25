import pickle
import operator
import codecs
import time


def load_matrix(filename):
    with open(filename, 'rb') as fp:
        W = pickle.load(fp)
    return W


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


def recommend(user, train, W):
    rank = {}
    interacted_items = train[user]
    for v, wuv in sorted(W[user].items(), key=operator.itemgetter(1), reverse=True):
        for i, rvi in train[v].items():
            if i in interacted_items:
                continue

            if i not in rank:
                rank[i] = 0
            rank[i] += wuv * rvi
    return rank


if __name__ == '__main__':
    train_file = '../data/SG_foursquare/train.txt'
    matrix_file = 'SG.matrix'

    user_logs = load_raw_logs(train_file, 0, 1)
    similarity = load_matrix(matrix_file)
    start_time =time.time()
    for user in user_logs:
        print(user)
        scores = recommend(user, user_logs, similarity)
        sorted_scores = sorted(scores.items(), key=operator.itemgetter(1), reverse=True)

    end_time = time.time()
    print("--- %s seconds ---" % (end_time - start_time))


