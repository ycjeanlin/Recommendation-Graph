import pickle
import codecs
import operator
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


def propagation(graph, node_id):
    pois = graph.neighbors(node_id)
    voters = {}
    for poi in pois:
        neighbor_list = graph.neighbors(poi)

        for n in neighbor_list:
            if n not in voters:
                voters[n] = 0
            voters[n] += 1

    return voters


if __name__ == '__main__':
    test_file = '../data/MovieLens/test.dat'
    graph_file = 'MovieLens.graph'
    output_file = 'user_coverage.dat'

    recommend_graph = load_graph(graph_file)

    test_logs = load_raw_logs(test_file, 0, 1)

    num_poi_dist = []
    max_poi_dist = []
    with codecs.open(output_file, 'w') as fw:
        poi_coverage = 0.8
        n_recall = 0
        user_percentage = {}
        user_miss = {}
        for user in test_logs:
            related_users = propagation(recommend_graph, user)

            sorted_users = sorted(related_users.items(), key=operator.itemgetter(1), reverse=True)

            num_hit = int(len(test_logs[user] * poi_coverage))
            help_user = 0
            num_user = len(sorted_users)
            for poi in test_logs[user]:
                for i in range(help_user, num_user):
                    if recommend_graph.has_edge(sorted_users[i][0], poi):
                        num_hit -= 1
                        help_user += 1
                        break

                if num_hit == 0 or help_user == num_user:
                    user_percentage[user] = help_user/num_user
                    user_miss[user] = float((len(test_logs[user]) - num_hit) / len(test_logs[user]))
                    break

        for user in user_percentage:
            fw.write(user + '\t' + user_percentage[user] + '\t' + user_miss[user] + '\n')


    fig = plt.figure()
    fig, (ax1, ax2) = plt.subplots(2, 1, sharey=True)
    ax1.hist(list(user_percentage.values()))
    ax2.hist(list(user_miss.values()))

    plt.show()

    print('Mission Complete')