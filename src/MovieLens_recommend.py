import pickle
import codecs
import operator
import numpy as np
import networkx as nx
import math
import random
import matplotlib.pyplot as plt


def load_graph(filename):
    with open(filename, 'rb') as fp:
        W = pickle.load(fp)
    return W


def load_raw_logs(input_file, user_index, item_index):
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


def giveup(degree_poi, degree_user):
    num1 = random.random()
    num2 = degree_user / float(degree_poi)
    #print(num1, num2)
    return num1 < num2


def propagation(graph, node_id, top_p):
    pois = graph.neighbors(node_id)
    voters = {}
    for poi in pois:
        neighbor_list = graph.neighbors(poi)

        for n in neighbor_list:
            if n not in voters:
                voters[n] = 0
            voters[n] += 1

    sorted_voters = sorted(voters.items(), key=operator.itemgetter(1), reverse=True)

    triggered_pois = {}
    threshold = int(len(sorted_voters) * top_p)
    for v in range(threshold):
        if sorted_voters[v][0] == node_id :
            continue

        for poi in graph.neighbors(sorted_voters[v][0]):

            if poi in graph.neighbors(node_id):
                continue

            if poi not in triggered_pois:
                triggered_pois[poi] = 0

            triggered_pois[poi] += 1

    return triggered_pois


def ground_truth_info(graph, user, item):
    graph.remove_edge(user, item)
    try:
        shortest_path_len = nx.shortest_path_length(graph, user, item)
        degree = graph.degree(item)
        poi_num_path = propagation(graph, user)
        num_path = poi_num_path[item]
    except:
        print('No Path')
        shortest_path_len = 0
        degree = 0
        num_path = 0

    graph.add_edge(user, item)

    return (degree, shortest_path_len, num_path)


def cal_entropy(dist):
    count = float(sum(dist.values()))
    n_classes = len(dist.keys())

    entropy = 0.0
    for key in dist:
        entropy -= dist[key] * math.log(dist[key]/count)

    return entropy / count

if __name__ == '__main__':
    train_file = '../data/MovieLens/train.dat'
    test_file = '../data/MovieLens/test.dat'
    graph_file = 'MovieLens.graph'
    output_file = 'exp_result.dat'

    recommend_graph = load_graph(graph_file)

    train_logs = load_raw_logs(train_file, 0, 1)
    test_logs = load_raw_logs(test_file, 0, 1)

    data_x1 = []
    data_x2 = []
    with codecs.open(output_file, 'w') as fw:

        for p in range(1):
            top_p = 0.1 + p * 0.01
            print('====== ', str(p), ' ======')
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
                    print('Recall:', float(n_recall / len(test_logs)))

                item_score = propagation(recommend_graph, user, top_p)

                sorted_pois = sorted(item_score.items(), key=operator.itemgetter(1), reverse=True)

                hit = 0
                for i in range(topk):
                    fw.write(sorted_pois[i][0] + '\t' + str(sorted_pois[i][1]) + '\n')
                    try:
                        if sorted_pois[i][0] in test_logs[user]:
                            hit += 1
                    except KeyError:
                        print(user, ' not found')
                '''
                print('Real')
                for poi in test_logs[user]:
                    try:
                        print(poi, item_score[poi])
                    except KeyError:
                        print(poi, ' not found')
                '''
                n_precision += topk
                if hit > 0:
                    n_recall += 1
                n_hit += hit
            data_x1.append((top_p, float(n_hit / n_precision)))
            data_x2.append((top_p, float(n_recall / len(test_logs))))
            #fw.write(str(top_p) + '\t' + str(float(n_hit) / float(n_precision)))
            #fw.write(str(top_p) + '\t' + str(float(n_recall / len(test_logs))))
            print('Precision:', float(n_hit) / float(n_precision))
            print('Recall:', float(n_recall / len(test_logs)))



    '''
            for poi in test_logs[user]:
                for n in recommend_graph.neighbors(poi):
                    if n in item_dist:
                        data_x.append(item_dist[n])

    '''

    fig = plt.figure()
    fig, (ax1, ax2) = plt.subplots(2, 1, sharey=True)
    x = [data_x1[i][0] for i in range(len(data_x1))]
    y = [data_x1[i][1] for i in range(len(data_x1))]
    ax1.scatter(x, y)
    x = [data_x2[i][0] for i in range(len(data_x2))]
    y = [data_x2[i][1] for i in range(len(data_x2))]
    ax2.scatter(x, y)


    ax1.set_xlabel('Precision')
    ax2.set_xlabel('Recall')

    plt.show()


    print('Mission Complete')
