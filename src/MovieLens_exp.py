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


def recommend(graph, node_id, top_p):
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


def exp1(graph, logs):
    with codecs.open(output_file, 'w') as fw:
        poi_coverage = 0.8
        user_percentage = {}
        user_miss = {}
        for user in logs:
            print(user)
            related_users = propagation(graph, user)

            sorted_users = sorted(related_users.items(), key=operator.itemgetter(1), reverse=True)

            num_hit = int(len(test_logs[user]) * poi_coverage)
            help_user = 0
            num_user = len(sorted_users)
            for poi in test_logs[user]:
                for i in range(help_user, num_user):
                    if recommend_graph.has_edge(sorted_users[i][0], poi):
                        num_hit -= 1
                        help_user += 1
                        break

                if num_hit == 0 or help_user == num_user:
                    user_percentage[user] = float(sorted_users[help_user-1][1])/float(sorted_users[0][1])
                    #user_percentage[user] = help_user/float(num_user)
                    user_miss[user] = float(len(test_logs[user]) - (len(test_logs[user]) * poi_coverage - num_hit)) / len(test_logs[user])
                    break

        for user in user_percentage:
            fw.write(user + '\t' + str(user_percentage[user]) + '\t' + str(user_miss[user]) + '\n')


    fig, (ax1, ax2) = plt.subplots(2, 1, sharey=True)
    ax1.hist(list(user_percentage.values()))
    ax2.hist(list(user_miss.values()))

    plt.show()


def exp2(graph, logs, out_file):
    with codecs.open(out_file, 'w') as fw:
        index = 0
        for user in logs:
            index += 1
            if (index % 100) == 0:
                print(index)

            pois = logs[user]
            related_users = propagation(graph, user)

            sorted_users = sorted(related_users.items(), key=operator.itemgetter(1), reverse=True)
            distribution = []
            for i in range(1, len(sorted_users)): #exclude user himself
                num_hit = 0
                for poi in pois:
                    if graph.has_edge(sorted_users[i][0], poi):
                        num_hit += 1

                distribution.append(float(num_hit / len(logs[user])))

            out_str = '\t'.join(format(x, "10.3f") for x in distribution)
            fw.write(user + '\t' + out_str + '\n')


def exp3(input_file, graph, topk):
    hit = 0
    total = 0
    with codecs.open(input_file, 'r') as fr:
        for row in fr:
            # load test file
            total += 1
            cols = row.strip().split('\t')
            user = cols[0]
            target_item = cols[1]

            # make recommendation for test user
            poi_scores = recommend(graph, user, 0.2)

            # rank the 1001 items within 1000 tested items
            test_item_score = {}
            for i in range(1, len(cols)):
                try:
                    test_item_score[cols[i]] = poi_scores[cols[i]]
                except:
                    test_item_score[cols[i]] = 0

            # check the target item whether it is in topk or not
            sorted_items = sorted(test_item_score.items(), key=operator.itemgetter(1), reverse=True)
            for i in range(topk):
                if target_item == sorted_items[i][0]:
                    hit += 1
                    break
    # Calculate recall of long-tail items
    print('Recall: ', float(hit / total))
    return float(hit / total)


if __name__ == '__main__':
    test_file = '../data/MovieLens/test.dat'
    graph_file = 'MovieLens.graph'
    output_file = 'user_coverage.dat'

    recommend_graph = load_graph(graph_file)

    test_logs = load_raw_logs(test_file, 0, 1)

    #exp1(recommend_graph,test_logs)
    #exp2(recommend_graph, test_logs, output_file)
    exp3(test_file, )



    print('Mission Complete')