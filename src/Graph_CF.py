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


def create_user_graph(user_log):
    print('Graph creating')
    graph = nx.Graph()
    index = 0
    for user, items in user_log.items():
        index += 1
        if index % 1000 == 0:
            print(index)
        if len(items) > 1:
            graph.add_node(user)

            for item in items:
                if item not in graph.nodes():
                    graph.add_node(item)
                graph.add_edge(user, item)

    return graph


def create_item_graph(user_log):
    print('Graph creating')
    graph = nx.Graph()

    print('User vs category')
    for user in user_log:
        graph.add_node(user)
        for item in user_log[user].keys():
            if item not in graph.nodes():
                graph.add_node(item)
            graph.add_edge(user, item)

    return graph


def write_graph(part_1, part_2, filename):
    print('Graph storing')
    with open(filename + '_1', 'wb') as fp:
        pickle.dump(part_1, fp)

    with open(filename + '_2', 'wb') as fp:
        pickle.dump(part_2, fp)


if __name__ == '__main__':
    train_file = '../data/yoochoose/click_logs_5.dat'
    graph_file = 'yoochoose_graph_5'

    start_time = time.time()
    session_item = load_raw_logs(train_file, 0, 2)
    item_session = load_raw_logs(train_file, 2, 0)
    end_time = time.time()
    '''
    print('number of session', len(user_logs))
    start_time = time.time()
    recommendation_graph = create_user_graph(user_logs)
    end_time = time.time()
    write_graph(recommendation_graph, graph_file)
    print("--- %s seconds ---" % (end_time - start_time))
    '''
    write_graph(session_item, item_session, graph_file)
    print("--- %s seconds ---" % (end_time - start_time))


