import networkx as nx
import codecs
from collections import Counter
import cPickle

def load_user_logs(log_file):
    print 'User logs loading'
    with codecs.open(log_file, 'r') as fr:
        user_logs = {}
        for row in fr:
            cols = row.strip().split('\t')
            user = cols[0]
            for i in range(1, len(cols)):
                weekday, time, POI, category = cols[i].strip('()').split(',')
                if user in user_logs:
                    user_logs[user].append((weekday, time, POI, category))
                else:
                    user_logs[user] = []
                    user_logs[user].append((weekday, time, POI, category))

    return user_logs


def load_user_preference(preference_file):
    print 'User preference loading'
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



def create_graph(user_logs, user_preference):
    graph = nx.Graph()

    print 'Session vs place'
    index = 0
    for user in user_logs:
        index += 1
        if index % 100 == 0:
            print index
        for log_time in user_logs[user]:
            cat_freq = Counter(user_logs[user][log_time])
            total = float(sum(cat_freq.values()))
            for cat in cat_freq:
                graph.add_node(user + '_' + log_time, type='session', time=log_time)
                #print cat, (cat not in graph.nodes())
                if cat not in graph.nodes():
                    graph.add_node(cat, type='cat')

                graph.add_edge(user + '_' + log_time, cat, weight=cat_freq[cat] / total)

    print 'User vs category'
    index = 0
    for user in user_preference:
        index += 1
        if index % 100 == 0:
            print index
        total = float(sum(user_preference[user].values()))
        for cat in user_preference[user]:
            graph.add_node(user, type='user')

            if cat not in graph.nodes():
                graph.add_node(cat, type='cat')
            graph.add_edge(user, cat, weight=user_preference[user][cat] / total)

    return graph


if __name__ == '__main__':
    user_activity = load_user_logs('NYC_time_train.dat')
    index = 0
    for user in user_activity:
        print user, user_activity[user]
        if index == 10:
            break
        index += 1

    user_profile = load_user_preference('user_preference.dat')
    index = 0
    for user in user_profile:
        print user, user_profile[user]
        if index == 10:
            break
        index += 1

    poi_category = load_hash_file('poi_to_category.dat')
    index = 0
    for poi in poi_category:
        print poi, poi_category[poi]
        if index == 10:
            break
        index += 1