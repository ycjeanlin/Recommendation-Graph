import codecs
import pickle
from math import sqrt
import operator
import time
import random


def load_raw_logs(input_file, session_index, item_index):
    '''
    load yoochoose-clicks.dat and yoochoose-buys.dat into a list of each session
    :param input_file: yoochoose-clicks.dat or yoochoose-buys.dat
    :param session_index: the index of the session id of a row in the data file
    :param item_index: the index of the item id of a row in the data file
    :return logs: lists of click logs divided by sessions
    '''
    with codecs.open(input_file, 'r') as fr:
        logs = {}
        index = 0
        for row in fr:
            cols = row.strip().split(',')
            index += 1
            if index % 1000000 == 0:
                print(index)
            session = cols[session_index]
            item = cols[item_index]
            if  session not in logs:
                logs[session] = []

            logs[session].append(item)

    return logs


def load_graph(filename):
    with open(filename, 'rb') as fp:
        W = pickle.load(fp)
    return W


def choose_next_node(candidates):
    return random.sample(candidates, 1)[0]


def CRRRW_no_update(s_i_edge, i_s_edge, clicked_set, top_k, start_item, steps, iter, candidate_set):
    recommend_items = []
    if start_item in i_s_edge:
        all_sessions = list(i_s_edge[start_item])
        count_iter = 0
        while count_iter < iter:
            node_type = 's'
            current_node = choose_next_node(all_sessions)
            count_step = 1
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


def convergence_sensor(pre_list, post_list):
    num_same = 0
    for i in post_list:
        if i in pre_list:
            num_same += 1
    return num_same


def adjust_iter(error, current_iter, min, delta):
    new_iter = current_iter

    new_iter += delta * error
    if new_iter < min:
        new_iter = min

    return new_iter


if __name__ == '__main__':
    buy_logs_file = '../data/yoochoose/buy_logs_5.dat'
    click_logs_file = '../data/yoochoose/click_logs_5.dat'
    ref_same = 3
    #init_iter = 50
    min_iter = 50
    delta_iter = 20 #teaking point

    print('Load logs')
    session_logs = load_raw_logs(click_logs_file, 0, 2)
    buy_logs = load_raw_logs(buy_logs_file, 0, 2)

    timing = {}
    print('Recommendation starts')
    for init_iter in range(50, 210, 30):
        fw = codecs.open('dynamic_iteration_%s.txt'%init_iter, 'w')
        print('=============', init_iter, '===============')
        print('Load graphs')
        session_item = load_graph('yoochoose_graph_1')
        item_session = load_graph('yoochoose_graph_2')

        index = 0
        total_iter = 0
        times = 0
        start_time = time.time()
        for s, logs in session_logs.items():
            index += 1
            if (index % 100000) == 0:
                print(index)

            if s in buy_logs:
                post = False
                buy_items = buy_logs[s]
                visited_items = set()
                pre_recom_list = []
                candidate_set = {}
                iteration = init_iter
                for i in logs:
                    if i in buy_items:
                        if not post:
                            post = True
                    else:
                        visited_items.add(i)
                        times += 1
                        total_iter += iteration
                        recommend_list, candidate_set = CRRRW_no_update(session_item, item_session, visited_items, 5, i, 2, iteration, candidate_set)
                        fw.write(s + '\t' + i + '\t' + str(post) + '\t' + str(iteration) + '\t' + ('\t').join(recommend_list) + '\n')
                        num_same = max(1, convergence_sensor(pre_recom_list, recommend_list))
                        error = ref_same - num_same
                        iteration = adjust_iter(error, iteration, min_iter, delta_iter)
                        pre_recom_list = recommend_list

            update_RG(session_item, item_session, s, logs)

        fw.close()
        end_time = time.time()
        timing[init_iter] = (int(total_iter / times), end_time - start_time)

    fw = codecs.open('exp_time.csv', 'w')
    for k in sorted(timing):
        fw.write('%s,%s,%s\n' % (k, timing[k][0], timing[k][1]))

    #write_graph(session_item, item_session, 'yoochoose_graph_update')
    print('EOP')


