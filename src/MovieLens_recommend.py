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


def load_user_logs(input_file, user_index, item_index):
    with codecs.open(input_file, 'r') as fr:
        train = {}
        for row in fr:
            cols = row.strip().split('\t')

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
    items = graph.neighbors(node_id)
    voters = {}
    for item in items:
        neighbor_list = graph.neighbors(item)

        for n in neighbor_list:
            if n not in voters:
                voters[n] = 0
            voters[n] += 1

    sorted_voters = sorted(voters.items(), key=operator.itemgetter(1), reverse=True)

    triggered_items = {}
    #threshold = int(len(sorted_voters) * top_p)
    for v in range(top_p):
        if v == len(sorted_voters):
            break

        if sorted_voters[v][0] == node_id :
            continue

        for item in graph.neighbors(sorted_voters[v][0]):

            if item in graph.neighbors(node_id):
                continue

            if item not in triggered_items:
                triggered_items[item] = 0

            triggered_items[item] += 1

    return triggered_items


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
    niche_items_file = '../data/MovieLens/niche_item.txt'
    graph_file = 'MovieLens.graph'
    output_file = 'recsys_result.dat'

    recommend_graph = load_graph(graph_file)

    #train_logs = load_user_logs(train_file, 0, 1)
    test_logs = load_user_logs(test_file, 1, 0)
    niche_items = set()
    with codecs.open(niche_items_file, 'r') as fr:
        for row in fr:
            niche_items.add(row.strip())

    for p in range(5, 101, 5):
        top_p = 0.1 + p * 0.05
        fw = codecs.open('top_' + str(p) + '.txt', 'w')
        print('====== ', str(p), ' ======')
        n_precision = 0
        n_recall = 0
        n_hit = 0
        index = 0
        for user in test_logs:
            index += 1
            #print(user)
            if((index % 1000) == 0):
                print(index)
                #print(user, hit, len(test_logs[user]))
                #print('Precision:', float(n_hit) / float(n_precision))
                #print('Recall:', float(n_hit / n_recall))
            if user not in niche_items or not recommend_graph.has_node(user):
                continue

            item_score = propagation(recommend_graph, user, p)

            sorted_items = sorted(item_score.items(), key=operator.itemgetter(1), reverse=True)

            fw.write(user)
            for i in range(50):
                if i == len(sorted_items):
                    break
                fw.write('\t' + sorted_items[i][0] + ':' + str(sorted_items[i][1]))
            fw.write('\n')
        fw.close()


    print('Mission Complete')
