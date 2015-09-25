import networkx as nx
import codecs
from collections import Counter
import pickle


def decode_time(encoded_time):
    weekday = encoded_time / 24
    time = encoded_time % 24

    return str(weekday), str(time)


def load_user_logs(log_file):
    print('User logs loading')
    with codecs.open(log_file, 'r') as fr:
        user_logs = {}
        for row in fr:
            cols = row.strip().split('\t')
            user = cols[0]
            for i in range(1, len(cols)):
                encoded_time, POI = cols[i].strip('()').split(',')
                weekday, time = decode_time(int(encoded_time))
                if user in user_logs:
                    if time in user_logs[user]:
                         user_logs[user][time].append(POI)
                    else:
                        user_logs[user][time] = []
                        user_logs[user][time].append(POI)
                else:
                    user_logs[user] = {}
                    user_logs[user][time] = []
                    user_logs[user][time].append(POI)

    return user_logs


def load_hash_file(hash_file):
    hash_table = {}

    with codecs.open(hash_file, 'r') as fr:
        for row in fr:
            cols = row.strip().split('\t')
            hash_table[cols[0]] = cols[1]

    return hash_table


def create_graph(user_logs, poi_hash):
    print('Graph creating')
    graph = nx.Graph()
    '''
    print('Session vs place')
    index = 0
    for user in user_logs:
        index += 1
        if index % 100 == 0:
            print(index)

        for t in user_logs[user]:

            graph.add_node(user + '_' + str(t), type='session', time=t)
            for poi in user_logs[user][t]:
                if poi not in graph.nodes():
                    graph.add_node(poi, type='poi', pos=poi_hash[poi])

                graph.add_edge(user + '_' + str(t), poi)
    '''
    print('User vs category')
    index = 0
    for user in user_logs:
        index += 1
        if index % 100 == 0:
            print(index)

        graph.add_node(user, type='user')
        for t in user_logs[user]:
            for poi in user_logs[user][t]:
                if poi not in graph.nodes():
                    graph.add_node(poi, type='poi', pos=poi_hash[poi])
                graph.add_edge(user, poi)

    return graph


def write_graph(graph, filename):
    print('Graph storing')
    with open(filename, 'wb') as fp:
        pickle.dump(graph, fp)


if __name__ == '__main__':
    user_activity = load_user_logs('SG_time_train.dat')

    poi_position = load_hash_file('poi_to_position.dat')

    foursquare_graph = create_graph(user_activity, poi_position)

    write_graph(foursquare_graph, 'SG_foursquare.graph')
