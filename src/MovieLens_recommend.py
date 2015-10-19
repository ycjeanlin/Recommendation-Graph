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


def propagation(graph, node_id):
    pois = graph.neighbors(node_id)
    voters = {}
    for poi in pois:
        neighbor_list = graph.neighbors(poi)
        if giveup(len(neighbor_list), len(pois)):
            continue

        for n in neighbor_list:
            if n not in voters:
                voters[n] = 0
            voters[n] += 1

    triggered_pois = {}
    for voter in voters:
        similarity = voters[voter]
        if voter == node_id:
            continue

        for poi in graph.neighbors(voter):
            if poi in graph.neighbors(node_id):
                continue

            if poi not in triggered_pois:
                triggered_pois[poi] = 0

            triggered_pois[poi] =+ similarity

    for poi in triggered_pois:
        triggered_pois[poi] = triggered_pois[poi] / graph.degree(poi)

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
    output_file = 'similarity_dist.dat'

    recommend_graph = load_graph(graph_file)

    train_logs = load_raw_logs(train_file, 0, 1)
    test_logs = load_raw_logs(test_file, 0, 1)

    num_poi_dist = []
    max_poi_dist = []
    with codecs.open(output_file, 'w') as fw:
        n_precision = 0
        n_recall = 0
        n_hit = 0
        topk = 5
        for user in test_logs:
            item_dist = propagation(recommend_graph, user)

            item_score = {}
            for item in item_dist:
                item_score[item] = item_dist[item]


            sorted_pois = sorted(item_score.items(), key=operator.itemgetter(1), reverse=True)

            hit = 0
            for i in range(topk):
                if sorted_pois[i][0] in test_logs[user]:
                    hit += 1

            n_precision += topk
            n_recall += len(test_logs[user])
            n_hit += hit


            print(user, hit, len(test_logs[user]))
            print('Precision:', float(n_hit) / float(n_precision))
            print('Recall:', float(n_hit) / float(n_recall))

    '''
            for poi in test_logs[user]:
                for n in recommend_graph.neighbors(poi):
                    if n in item_dist:
                        data_x.append(item_dist[n])



    fig = plt.figure()
    fig, (ax1) = plt.subplots(1, 1, sharey=True)
    ax1.hist(data_x)
    #ax2.hist(data_y)


    ax1.set_xlabel('User Similarity')

    plt.show()
    '''
    print('Mission Complete')








