import pickle
import codecs
import operator
import matplotlib.pyplot as plt
from math import sqrt
import random
import networkx as nx


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
                    if graph.has_edge(sorted_users[i][0], poi):
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


def exp_niche_item_recall(input_file, graph, topk):
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


def exp6(graph, exp_logs):
    '''
    Count the number of paths between a user and his related items
    '''
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

            #item_paths = recommend(graph, user, 1)
            try:
                for p in nx.all_shortest_paths(graph,source=user,target=item):
                    fw.write(str(p) + '\n')
                    #print(p)
            except:

                print(user, item, 'no path')
            # write # of paths into output file
            '''
            hit = 0
            for i in item_paths:
                if i == item:
                    hit = 1
                    fw.write(user + '\t' + i + '\t1\t' + str(item_paths[i]) + '\n')
                else:
                    fw.write(user + '\t' + i + '\t0\t' + str(item_paths[i]) + '\n')

            if hit == 0:
                fw.write(user + '\t' + i + '\t1\t0\n')
            '''
            graph.add_edge(user, item)
            assert graph.has_edge(user, item), '[Error] Edge does not exist'

    fw.close()


def exp7(graph, exp_logs):
    '''
    Calculate the triggered users proportion and the triggered poi proportion
    Output user proportion and item proportion to a file
    '''
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


def exp_popularity(item_logs, result_file, out_file):
    popularity = {}
    with codecs.open(result_file, 'r') as fr:
        for row in fr:
            cols = row.strip().split('\t')
            for i in range(1, 6):
                if i == len(cols):
                    break
                item, score = cols[i].split(':')
                if item not in popularity:
                    try:
                        popularity[item] = len(item_logs[item])
                    except:
                        popularity[item] = 1

    fw = codecs.open(out_file, 'w')
    for item, p in popularity.items():
        fw.write(item + '\t' + str(p) + '\n')

    fw.close()


def exp_precision(test_logs, item_logs, result_file, out_file):
    n_precision = 0
    n_hit = 0
    popularity = {}
    with codecs.open(result_file, 'r') as fr:
        for row in fr:
            cols = row.strip().split('\t')
            user = cols[0]
            for i in range(1, 6):
                if i == len(cols):
                    break
                item, score = cols[i].split(':')
                if item in test_logs[user]:
                    n_hit += 1
                    if item not in popularity:
                        popularity[item] = len(item_logs[item])

            n_precision += 5

    fw = codecs.open(out_file, 'w')
    for item, p in popularity.items():
        fw.write(item + '\t' + str(p) + '\n')

    fw.close()

    return float(n_hit / n_precision)


def exp_diversity(out_file):
    diversity = {}
    for i in range(5, 51, 5):
        items = set()
        with codecs.open('exp_popularity_hit_'+str(i)+'.txt', 'r') as fr:
            for row in fr:
                cols = row.strip().split('\t')
                items.add(cols[0])
        diversity[i] = len(items)

    fw = codecs.open(out_file, 'w')
    for i in range(5, 51, 5):
        fw.write(str(i) + '\t' + str(diversity[i]) + '\n')

    fw.close()


def exp_item_recommended_times(item_logs, test_logs, result_file, out_file):
    times = {}
    for i in range(5, 51, 5):
        with codecs.open(result_file + '_top_' + str(i)+'.txt', 'r') as fr:
            for row in fr:
                cols = row.strip().split('\t')
                user = cols[0]
                for j in range(1, 6):
                    if j == len(cols):
                        break
                    item, score = cols[j].split(':')
                    if item not in test_logs[user]:
                        continue

                    if item not in times:
                        times[item] = {}

                    if i not in times[item]:
                        times[item][i] = 0

                    times[item][i]  += 1

    fw = codecs.open(out_file, 'w')
    for item, counts in times.items():
        fw.write(item)
        for topk in range(5, 51, 5):
            try:
                fw.write(',' + str(times[item][topk]))
            except:
                fw.write(',0')
        fw.write(',' + str(len(item_logs[item])) + '\n')


    fw.close()


if __name__ == '__main__':
    train_file = '../data/MovieLens/train.dat'
    test_file = '../data/MovieLens/test.dat'
    graph_file = 'MovieLens.graph'
    output_file = 'user_coverage.dat'

    recommend_graph = load_graph(graph_file)
    test_logs = load_raw_logs(train_file, 0, 1)
    #item_logs = load_raw_logs(train_file, 1, 0)

    #test_logs = load_raw_logs(test_file, 1, 0)
    #exp1(recommend_graph,test_logs)
    #exp2(recommend_graph, test_logs, output_file)
    #exp3(test_file, recommend_graph, 5)
    #exp4(test_file, recommend_graph, 'exp4_result.dat')
    #exp5(recommend_graph, test_logs)
    exp6(recommend_graph, test_logs)
    #exp7(recommend_graph, test_logs)
    '''
    fw = codecs.open('exp_precision.txt', 'w')
    for i in range(5, 101, 5):
        fw.write(str(i) + '\t' + str(exp_precision(item_logs, test_logs, 'top_'+ str(i) + '.txt', 'exp_popularity_hit_'+ str(i) + '.txt')) + '\n')
        exp_popularity(test_logs, 'top_'+ str(i) + '.txt', 'exp_popularity_'+ str(i) + '.txt')
    fw.close()
    '''
    #exp_precision(test_logs, item_logs, 'train_sorted.dat', 'exp_precision_5.txt')
    #exp_popularity(item_logs, 'CF_weight_rating_top_5.txt', 'item_popularity.txt')
    #exp_item_recommended_times(item_logs, test_logs, 'CF_weight_rating', 'exp_times_weight_rating_hit.csv')
    #exp_diversity('exp_diversity_hit.txt')

    print('Mission Complete')