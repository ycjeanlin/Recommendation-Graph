import pickle
import operator
import codecs
import random
import time
from math import sqrt


def load_conv_log(input_file, user_index, item_index):
    '''
    ' load the logs that is converted by preprocess
    '''
    logs = {}
    index = 0
    with codecs.open(input_file, 'r') as fr:
        for row in fr:
            index += 1
            if (index % 1000) == 0:
                print(index)

            cols = row.strip().split(',')

            session = cols[user_index]
            if session not in logs:
                logs[session] = []

            logs[session].append(cols[item_index])

    return logs


def choose_next_node(candidates):
    return random.sample(candidates, 1)[0]


def CRRCF_no_update(s_i_edge, i_s_edge, clicked_set, top_k, target_item, candidate_set):
    recommend_items = []

    if target_item in i_s_edge:
        sessions = i_s_edge[target_item]
        pair_count = {}
        for s in sessions:
            item_list = s_i_edge[s]

            for i in item_list:
                if i not in pair_count:
                    pair_count[i] = 0
                pair_count[i] += 1

        speedup = {}
        degree1 = len(sessions)
        for i in pair_count:
            degree2 = len(i_s_edge[i])
            if degree2 not in speedup:
                speedup[degree2] = sqrt(degree1 * degree2)
            if i not in candidate_set:
                candidate_set[i] = 0
            candidate_set[i] += float(pair_count[i] / speedup[degree2])

        sorted_voters = sorted(candidate_set.items(), key=operator.itemgetter(1), reverse=True)

        rank = 0
        v = 0
        while rank < top_k:
            if v == len(sorted_voters):
                break

            if sorted_voters[v][0] not in clicked_set:
                recommend_items.append(sorted_voters[v][0])
                rank += 1
            v += 1

    return recommend_items, candidate_set



def CRRRW_no_update(s_i_edge, i_s_edge, clicked_set, top_k, start_item, steps, iter, candidate_set):
    recommend_items = []
    if start_item not in i_s_edge:
        return recommend_items, candidate_set

    all_sessions = list(i_s_edge[start_item])
    count_iter = 0
    while count_iter < iter:
        count_step = 0
        node_type = 's'
        current_node = choose_next_node(all_sessions)
        count_step += 1
        while count_step < steps:
            if node_type == 's':
                current_node = choose_next_node(s_i_edge[current_node])
                node_type = 'i'
            else:
                current_node = choose_next_node(i_s_edge[current_node])
                node_type = 's'

            count_step += 1

        if current_node not in candidate_set:
            candidate_set[current_node] = 0
        candidate_set[current_node] += 1
        count_iter += 1

    sorted_items = sorted(candidate_set.items(), key=operator.itemgetter(1), reverse=True)

    rank = 0
    v = 0
    while rank < top_k:
        if v == len(sorted_items):
            break

        if sorted_items[v][0] not in clicked_set:
            recommend_items.append(sorted_items[v][0])
            rank += 1
        v += 1

    return recommend_items, candidate_set


def update_RG(s_i_edge, i_s_edge, s_id, clicked_set):
    if s_id not in s_i_edge:
        s_i_edge[s_id] = set(clicked_set)

    for i in s_i_edge[s_id]:
        if i not in i_s_edge:
            i_s_edge[i] = set()
        i_s_edge[i].add(s_id)


def load_graph(filename):
    with open(filename, 'rb') as fp:
        W = pickle.load(fp)
    return W


if __name__ == '__main__':
    test_file = '../data/CA_foursquare/conv_test.dat'
    #train_file = '../SG_gowalla/conv_train.dat'
    output_path = 'D:\\Exp Result\\CA_foursquare\\CRRRW\\'

    print('Load logs')
    #train_logs = load_conv_log(train_file, 0, 1)
    test_logs = load_conv_log(test_file, 0, 1)

    index = 0
    timing = {}
    print('Recommendation starts')
    for iteration in range(30, 400, 30):
    #for topk in [5,10,15,20,25,30]:
        fw = codecs.open(output_path + 'iteration_' + str(iteration) + '.txt', 'w')
        #fw = codecs.open(output_path + 'top_' + str(topk) + '.txt', 'w')
        print('=============', iteration, '===============')
        #print('=============', topk, '===============')
        print('Load graphs')
        session_item = load_graph('CA_foursquare_graph_1')
        item_session = load_graph('CA_foursquare_graph_2')
        index = 0
        start_time = time.time()
        for s, logs in test_logs.items():
            if len(logs) > 1:
                candidate_set = {}
                index += 1
                if (index % 1000) == 0:
                    print(index)

                visited_items = set()
                for i in range(0, len(logs)-1):
                    visited_items.add(logs[i])
                    #recommend_list = SRRCF(session_item, item_session, visited_items, topk, i, s)
                    #recommend_list, candidate_set = CRRCF_no_update(session_item, item_session, visited_items, topk, logs[i], candidate_set)
                    #recommend_list = SRRRW(session_item, item_session, visited_items, 5, i, s, 2, iteration)
                    recommend_list, candidate_set = CRRRW_no_update(session_item, item_session, visited_items, 5, logs[i], 2, iteration, candidate_set)
                    #print(logs[i])
                    fw.write(s + '\t' + logs[i] + '\t' + ('\t').join(recommend_list) + '\n')

                update_RG(session_item, item_session, s, logs)

        fw.close()
        end_time = time.time()
        timing[iteration] = end_time - start_time
        #timing[topk] = end_time - start_time

    fw = codecs.open(output_path + 'exp_time.csv', 'w')
    for k in sorted(timing):
        fw.write('%s, %s\n' % (k, timing[k]))

    #write_graph(session_item, item_session, 'yoochoose_graph_update')
    print('EOP')