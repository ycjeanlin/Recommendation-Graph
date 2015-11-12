import codecs
import math
import pickle
import networkx as nx
import time


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
                train[user] = {}
                train[user][item] = 1

            if item not in train[user]:
                train[user][item] = 1

    return train


def create_user_graph(user_log):
    print('Graph creating')
    graph = nx.Graph()

    print('User vs category')
    for user in user_logs:
        graph.add_node(user)
        for item in user_logs[user].keys():
            if item not in graph.nodes():
                graph.add_node(item)
            graph.add_edge(user, item)

    return graph


def create_item_graph(user_log):
    print('Graph creating')
    graph = nx.Graph()

    print('User vs category')
    for user in user_logs:
        graph.add_node(user)
        for item in user_logs[user].keys():
            if item not in graph.nodes():
                graph.add_node(item)
            graph.add_edge(user, item)

    return graph


def write_graph(graph, filename):
    print('Graph storing')
    with open(filename, 'wb') as fp:
        pickle.dump(graph, fp)


if __name__ == '__main__':
    train_file = '../data/MovieLens/train.dat'
    graph_file = 'MovieLens.graph'

    user_logs = load_raw_logs(train_file, 0, 1)
    start_time = time.time()
    recommendation_graph = create_user_graph(user_logs)
    end_time = time.time()
    write_graph(recommendation_graph, graph_file)
    print("--- %s seconds ---" % (end_time - start_time))


