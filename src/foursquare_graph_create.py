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


def load_user_preference(preference_file):
    print('User preference loading')
    with codecs.open(preference_file, 'r') as fr:
        user_preference = {}
        for row in fr:
            cols = row.strip().split('\t')
            user = cols[0]
            for i in range(1, len(cols)):
                cat, count = cols[i].strip('()').split(',')
                if user in user_preference:
                    user_preference[user][cat] = int(count)
                else:
                    user_preference[user] = {}
                    user_preference[user][cat] = int(count)

    return user_preference


def load_hash_file(hash_file):
    hash_table = {}

    with codecs.open(hash_file, 'r') as fr:
        for row in fr:
            cols = row.strip().split('\t')
            hash_table[cols[0]] = cols[1]

    return hash_table


def create_graph(user_logs, poi_hash, user_preference):
    print('Graph creating')
    graph = nx.Graph()

    print('Session vs place')
    index = 0
    for user in user_logs:
        index += 1
        if index % 100 == 0:
            print(index)

        for t in user_logs[user]:
            cat_list = []
            for poi in user_logs[user][t]:
                cat_list.append(poi_hash[poi])

            cat_freq = Counter(cat_list)
            total = float(sum(cat_freq.values()))

            graph.add_node(user + '_' + str(t), type='session', time=t)
            for poi in user_logs[user][t]:
                #print cat, (cat not in graph.nodes())
                if poi not in graph.nodes():
                    graph.add_node(poi, type='poi')

                graph.add_edge(user + '_' + str(t), poi, weight=cat_freq[poi_hash[poi]] / total)

    print('User vs category')
    index = 0
    for user in user_logs:
        index += 1
        if index % 100 == 0:
            print(index)

        total = float(sum(user_preference[user].values()))
        graph.add_node(user, type='user')
        for t in user_logs[user]:
            for poi in user_logs[user][t]:
                if poi not in graph.nodes():
                    graph.add_node(poi, type='poi')
                graph.add_edge(user, poi, weight=user_preference[user][poi_hash[poi]] / total)

    return graph


def write_graph(graph, filename):
    print('Graph storing')
    with open(filename, 'wb') as fp:
        pickle.dump(graph, fp)


if __name__ == '__main__':
    user_activity = load_user_logs('SG_time_train.dat')

    user_profile = load_user_preference('user_preference.dat')

    poi_category = load_hash_file('occurence.dat')

    foursquare_graph = create_graph(user_activity, poi_category, user_profile)

    write_graph(foursquare_graph, 'foursquare_SG.graph')
