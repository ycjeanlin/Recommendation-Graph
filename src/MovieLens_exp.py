import pickle
import codecs
import operator
import matplotlib.pyplot as plt
from math import sqrt
import random


def load_graph(filename):
    with open(filename, 'rb') as fp:
        W = pickle.load(fp)
    return W


def load_raw_logs(input_file, user_index, item_index):
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


def propagation(graph, node_id):
    pois = graph.neighbors(node_id)
    voters = {}
    for poi in pois:
        neighbor_list = graph.neighbors(poi)
        punish = float(len(neighbor_list))
        for n in neighbor_list:
            if n not in voters:
                voters[n] = 0
            voters[n] += 1 / punish

    return voters


def recommend(graph, node_id, top_p):
    # TODO need to modify for 80/20 expirement
    pois = graph.neighbors(node_id)
    voters = {}
    for poi in pois:
        neighbor_list = graph.neighbors(poi)

        for n in neighbor_list:
            if n not in voters:
                voters[n] = 0
            voters[n] += 1
    '''
    for v in voters:
        voters[v] = float(voters[v] / len(graph.neighbors(v)))
    '''

    #sorted_voters = sorted(voters.items(), key=operator.itemgetter(1), reverse=True)

    triggered_pois = set()
    #threshold = int(len(sorted_voters) * top_p)
    for v in voters:
        if v == node_id :
            continue

        for poi in graph.neighbors(v):
            '''
            if poi in graph.neighbors(node_id):
                continue


            if poi not in triggered_pois:
                triggered_pois[poi] = 0

            triggered_pois[poi] += 1
            '''
            triggered_pois.add(poi)
            if len(triggered_pois) == 3706:
                print('break')
                break

    return len(voters), triggered_pois


def exp1(graph, logs, output_file):
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
            if (total % 100) == 0:
                print(total, hit)

            cols = row.strip().split('\t')
            user = cols[0]
            target_item = cols[1]

            # make recommendation for test user
            poi_scores = recommend(graph, user, 0.15)

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
                print(poi_scores[target_item], sorted_items[i][1])
                if target_item == sorted_items[i][0]:
                    hit += 1
                    break
    # Calculate recall of long-tail items
    print('Recall: ', float(hit / total))
    return float(hit / total)


def exp4(input_file, graph, output_file):
    with codecs.open(input_file, 'r') as fr:
        fw = codecs.open(output_file, 'w')
        index = 0
        for row in fr:

            index += 1
            if (index % 100) == 0:
                print(index)

            # load test file
            cols = row.strip().split('\t')
            user = cols[0]
            target_item = cols[2]

            related_users = propagation(graph, user)
            sorted_users = sorted(related_users.items(), key=operator.itemgetter(1), reverse=True)
            top_20_user = int(len(sorted_users) * 0.2)

            #user_items = len(graph.neighbors(user))
            fw.write(user)
            for i in range(top_20_user):
                #check whether has relation with target item
                if graph.has_edge(sorted_users[i][0], target_item):
                    fw.write('\t' + str(float(sorted_users[i][1])))
            fw.write('\n')


def exp5(graph, logs):
    with codecs.open('exp5_result.txt', 'w') as fw:
        for u in logs:
            print(u)
            activeness = len(logs[u])
            for item in logs[u]:
                try:
                    popularity = graph.degree(item)
                    fw.write(str(activeness) + '\t' + str(popularity) + '\n')
                except:
                    print('Error')


def exp6(graph, exp_logs):
    # randomly sample 10 users for the experiment
    sample_users = [ list(exp_logs.keys())[i] for i in random.sample(range(len(exp_logs)), 10)]

    fw = codecs.open('exp6_result.txt', 'w')
    for user in sample_users:
        print(user)
        # get the relevant items
        relevant_items = exp_logs[user]

        for item in relevant_items:
            graph.remove_edge(user,item)
            assert not graph.has_edge(user, item), '[Error] Edge exists'

            item_paths = recommend(graph, user, 1)

            # write # of paths into output file
            hit = 0
            for i in item_paths:
                if i == item:
                    hit = 1
                    fw.write(user + '\t' + i + '\t1\t' + str(item_paths[i]) + '\n')
                else:
                    fw.write(user + '\t' + i + '\t0\t' + str(item_paths[i]) + '\n')

            if hit == 0:
                fw.write(user + '\t' + i + '\t1\t0\n')

            graph.add_edge(user, item)
            assert graph.has_edge(user, item), '[Error] Edge does not exist'

    fw.close()


def exp7(graph, exp_logs):
    fw = codecs.open('exp7_result.txt', 'w')
    index = 0
    for user in exp_logs:
        index += 1
        #print(user)
        if (index % 100) == 0:
            print(index)
        num_users, pois = recommend(graph, user, 1)
        p_user = float(num_users / 6040)
        p_item = float(len(pois) / 3706)
        fw.write(str(p_user) + '\t' + str(p_item) + '\n')

    fw.close()

if __name__ == '__main__':
    exp_file = '../data/MovieLens/train.dat'
    graph_file = 'MovieLens.graph'
    output_file = 'user_coverage.dat'

    recommend_graph = load_graph(graph_file)

    test_logs = load_raw_logs(exp_file, 0, 1)

    #exp1(recommend_graph,test_logs)
    #exp2(recommend_graph, test_logs, output_file)
    #exp3(test_file, recommend_graph, 5)
    #exp4(test_file, recommend_graph, 'exp4_result.dat')
    #exp5(recommend_graph, test_logs)
    #exp6(recommend_graph, test_logs)
    exp7(recommend_graph, test_logs)

    print('Mission Complete')