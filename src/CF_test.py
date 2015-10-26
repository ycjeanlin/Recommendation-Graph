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

def load_logs(input_file, user_index, item_index):
    with codecs.open(input_file, 'r') as fr:
        train = {}
        index = 0
        for row in fr:
            cols = row.strip().split('\t')
            index += 1
            if index % 10000 == 0:
                print(index)
            user = cols[user_index]
            item = cols[item_index]
            if  user not in train:
                train[user] = set()

            train[user].add(item)

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
    train_file = '../data/MovieLens/train.dat'
    test_file = '../data/MovieLens/test.dat'
    matrix_file = 'MovieLens.matrix'

    train_logs = load_raw_logs(train_file, 0, 1)
    test_logs = load_logs(test_file, 0, 1)
    similarity = load_matrix(matrix_file)
    start_time =time.time()
    n_precision = 0
    n_recall = 0
    n_hit = 0
    topk = 5
    index = 0
    for user in train_logs:
        index += 1
        #print(user)
        if((index % 100) == 0):
            print(index)
            print(user, hit, len(test_logs[user]))
            print('Precision:', float(n_hit) / float(n_precision))
            print('Recall:', float(n_hit / n_recall))

        scores = recommend(user, train_logs, similarity)
        sorted_scores = sorted(scores.items(), key=operator.itemgetter(1), reverse=True)

        hit = 0
        for i in range(topk):
            try:
                if sorted_scores[i][0] in test_logs[user]:
                    hit += 1
            except KeyError:
                print(user, ' not found')

        n_precision += topk
        n_recall += len(test_logs[user])
        n_hit += hit

    end_time = time.time()
    print("--- %s seconds ---" % (end_time - start_time))


