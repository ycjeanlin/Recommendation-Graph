import pickle
import operator
import codecs
import time


def load_matrix(filename):
    print('Load matrix')
    with open(filename, 'rb') as fp:
        W = pickle.load(fp)
    return W


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


def load_raw_logs(test, input_file, user_index, item_index, rating_index):
    print('Load user logs')
    with codecs.open(input_file, 'r') as fr:
        train = {}
        for row in fr:
            cols = row.strip().split('::')

            user = cols[user_index]
            item = cols[item_index]
            rating = float(cols[rating_index])
            if  user not in train:
                train[user] = {}

            if item not in train[user]:
                if user not in test or (user in test and item not in test[user]):
                    train[user][item] = rating

    return train


def recommend(user, train, W, topk):
    rank = {}
    normalize = {}
    interacted_items = train[user]
    for v, wuv in sorted(W[user].items(), key=operator.itemgetter(1), reverse=True)[:topk]:
        #print(v, wuv)
        for i, rvi in train[v].items():
            if i in interacted_items:
                continue

            if i not in rank:
                rank[i] = 0
                normalize[i] = 0
            '''
            if i == target:
                print(i, wuv, rvi)
            '''
            rank[i] += 1
            normalize[i] += wuv
    '''
    for i in rank:
        rank[i] = rank[i] / normalize[i]
    '''
    return rank


if __name__ == '__main__':
    train_file = '../data/MovieLens/train.dat'
    test_file = '../data/MovieLens/test.dat'
    matrix_file = 'MovieLens.matrix'

    test_logs = load_train_logs(test_file, 0, 1, 2)
    train_logs = load_train_logs(train_file, 0, 1, 2)
    similarity = load_matrix(matrix_file)

    #topk = 20

    precision = []

    for topk in range(5, 51, 5):
        start_time =time.time()
        n_precision = 0
        n_recall = 0
        n_hit = 0
        index = 0
        fw = codecs.open('CF_no_weight_top_' + str(topk) + '.txt', 'w')
        for user in test_logs:
            index += 1
            #print(user, target_item)
            '''
            if((index % 100) == 0):
                print(index)
                #print(user, hit, len(test_logs[user]))
                print('Precision:', float(n_hit / n_precision))
                #print('Recall:', float(n_hit / n_recall))
            '''
            predict_ratings = recommend(user, train_logs, similarity, topk)

            '''
            try:
                print(predict_ratings[target_item])
            except KeyError:
                print('KeyError')
            scores = {}
            for item in test_logs[user]:
                if item in predict_ratings:
                    scores[item] = predict_ratings[item]
                else:
                    scores[item] = 0
            '''

            sorted_scores = sorted(predict_ratings.items(), key=operator.itemgetter(1), reverse=True)

            fw.write(user)
            for i in range(50):
                if i == len(sorted_scores):
                    break
                fw.write('\t' + sorted_scores[i][0] + ':' + str(sorted_scores[i][1]))

                '''
                if sorted_scores[i][0] in test_logs[user]:
                    n_hit += 1
                '''
            fw.write('\n')
            n_precision += topk
            n_recall += 1

        fw.close()
        precision.append(float(n_hit / n_precision))
        #print('Recall:', float(n_hit / n_recall))
        print('Precision:', float(n_hit / n_precision))

        end_time = time.time()
    '''
    with codecs.open('CF_test_exp.csv', 'w') as fw:
        for i in range(len(precision)):
            fw.write(str(i * 5 + 5) + ',' + str(precision[i]) + '\n')
    '''
    print("--- %s seconds ---" % (end_time - start_time))


