import codecs
import pickle
from math import sqrt
import operator
import time
import random
import logging


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


def SRRCF_no_update(s_i_edge, i_s_edge, clicked_set, top_k, target_item):
    recommend_items = []
    if target_item not in i_s_edge:
        return recommend_items

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
        pair_count[i] = float(pair_count[i] / speedup[degree2])

    sorted_voters = sorted(pair_count.items(), key=operator.itemgetter(1), reverse=True)

    rank = 0
    v = 0
    while rank < top_k:
        if v == len(sorted_voters):
            break

        if sorted_voters[v][0] not in clicked_set:
            recommend_items.append(sorted_voters[v][0])
            rank += 1
        v += 1

    return recommend_items


def SRRCF(s_i_edge, i_s_edge, clicked_set, top_k, target_item, session_id):
    recommend_items = []
    if target_item not in i_s_edge:
        return recommend_items

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
        pair_count[i] = float(pair_count[i] / speedup[degree2])

    sorted_voters = sorted(pair_count.items(), key=operator.itemgetter(1), reverse=True)

    rank = 0
    v = 0
    while rank < top_k:
        if v == len(sorted_voters):
            break

        if sorted_voters[v][0] not in clicked_set:
            recommend_items.append(sorted_voters[v][0])
            rank += 1
        v += 1

    return recommend_items


def CRRCF_no_update(s_i_edge, i_s_edge, clicked_set, top_k, target_item, session_id, candidate_set):
    recommend_items = []
    item_score = {}

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


def CRRCF(s_i_edge, i_s_edge, clicked_set, top_k, target_item, session_id, candidate_set):
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


def choose_next_node(candidates):
    return random.sample(candidates, 1)[0]


def SRRRW_no_update(s_i_edge, i_s_edge, clicked_set, top_k, start_item, steps, iter):
    recommend_items = []
    if start_item not in i_s_edge:
        return recommend_items

    visit_count = {}
    all_sessions = list(i_s_edge[start_item])
    while iter > 0:
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

        #assert node_type == 'i', 'Error Recommendation'
        if current_node not in visit_count:
            visit_count[current_node] = 0
        visit_count[current_node] += 1
        iter -= 1

    sorted_voters = sorted(visit_count.items(), key=operator.itemgetter(1), reverse=True)

    rank = 0
    v = 0
    while rank < top_k:
        if v == len(sorted_voters):
            break

        if sorted_voters[v][0] not in clicked_set:
            recommend_items.append(sorted_voters[v][0])
            rank += 1
        v += 1

    return recommend_items


def itemset_based_random_walk(s_i_edge, i_s_edge, clicked_set, top_k, steps, iter):
    recommend_items = []
    visit_count = {}
    all_sessions = []
    for ci in clicked_set:
        if ci in i_s_edge:
            all_sessions.extend(i_s_edge[ci])

    if len(all_sessions) > 0:
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

            assert node_type == 'i', 'Error Recommendation'
            if current_node not in visit_count:
                visit_count[current_node] = 0
            visit_count[current_node] += 1
            count_iter += 1

        sorted_items = sorted(visit_count.items(), key=operator.itemgetter(1), reverse=True)

        rank = 0
        v = 0
        while rank < top_k:
            if v == len(sorted_items):
                break

            if sorted_items[v][0] not in clicked_set:
                recommend_items.append(sorted_items[v][0])
                rank += 1
            v += 1

    return recommend_items


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


def continue_items_based_random_walk(s_i_edge, i_s_edge, clicked_set, top_k, start_item, steps):
    recommend_items = []
    if start_item not in i_s_edge:
        return recommend_items

    all_sessions = list(i_s_edge[start_item])

    visit_count = {}
    count_step = 0
    node_type = 'i'
    current_node = start_item
    while count_step < steps:
        if node_type == 's':
            current_node = choose_next_node(list(s_i_edge[current_node]))
            node_type = 'i'
        else:
            if current_node not in visit_count:
                visit_count[current_node] = 0
            visit_count[current_node] += 1
            current_node = choose_next_node(list(i_s_edge[current_node]))
            node_type = 's'

        count_step += 1


    sorted_items = sorted(visit_count.items(), key=operator.itemgetter(1), reverse=True)

    rank = 0
    v = 0
    while rank < top_k:
        if v == len(sorted_items):
            break

        if sorted_items[v][0] not in clicked_set:
            recommend_items.append(sorted_items[v][0])
            rank += 1
        v += 1

    return recommend_items


def CRRRW_commute_time_no_update(s_i_edge, i_s_edge, clicked_set, top_k, start_item, steps, iter_go, iter_back, candidate_set):
    recommend_items = []
    if start_item not in i_s_edge:
        return recommend_items, candidate_set

    all_sessions = list(i_s_edge[start_item])
    count_iter = 0
    reach_times = {}
    while count_iter < iter_go: #TODO tweaking points
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

        if current_node not in reach_times:
            reach_times[current_node] = 0
        reach_times[current_node] += 1
        count_iter += 1

    sorted_items = sorted(reach_times.items(), key=operator.itemgetter(1), reverse=True)
    candidate_items = [sorted_items[i][0] for i in range(len(sorted_items)) if i < top_k*2 ] #TODO tweaking points

    for candidate in candidate_items:
        all_sessions = list(i_s_edge[candidate])
        count_iter = 0
        while count_iter < iter_back: #TODO tweaking points
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

            if current_node in clicked_set:
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


def write_graph(part_1, part_2, filename):
    print('Graph storing')
    with open(filename + '_1', 'wb') as fp:
        pickle.dump(part_1, fp)

    with open(filename + '_2', 'wb') as fp:
        pickle.dump(part_2, fp)


def recommend_CRRrw(session_logs, buy_logs):
    timing = {}
    print('Recommendation starts')
    for iteration in range(30, 50, 30):
        fw = codecs.open('iteration_' + str(iteration) + '_2_step.txt', 'w')
        print('=============', iteration, '===============')
        print('Load graphs')
        session_item = load_graph('yoochoose_graph_1')
        item_session = load_graph('yoochoose_graph_2')
        index = 0
        start_time = time.time()
        for s, logs in session_logs.items():
            index += 1
            if (index % 100000) == 0:
                print(index)

            if s in buy_logs:
                post = False
                buy_items = buy_logs[s]
                candidate_set = {}
                visited_items = set()
                for i in logs:
                    if i in buy_items:
                        if not post:
                            post = True
                    #else:
                    visited_items.add(i)
                    #recommend_list = SRRRW(session_item, item_session, visited_items, 5, i, s, 2, iteration)
                    recommend_list, candidate_set = CRRRW_no_update(session_item, item_session, visited_items, 5, i, 2, iteration, candidate_set)
                    fw.write(s + '\t' + i + '\t' + str(post) + '\t' + ('\t').join(recommend_list) + '\n')

            #update_RG(session_item, item_session, s, logs)

        fw.close()
        end_time = time.time()
        timing[iteration] = end_time - start_time

    fw = codecs.open('exp_time.csv', 'w')
    for k in sorted(timing):
        fw.write('%s, %s\n' % (k, timing[k]))


def recommend_CRRcf(session_logs, buy_logs):
    timing = {}
    print('Recommendation starts')
    for topk in [5,5,10,15,20,25,30]:
        fw = codecs.open('top_' + str(topk) + '.txt', 'w')
        print('=============', topk, '===============')
        print('Load graphs')
        session_item = load_graph('yoochoose_graph_1')
        item_session = load_graph('yoochoose_graph_2')
        index = 0
        start_time = time.time()
        for s, logs in session_logs.items():
            index += 1
            if (index % 100000) == 0:
                print(index)

            if s in buy_logs:
                post = False
                buy_items = buy_logs[s]
                candidate_set = {}
                visited_items = set()
                for i in logs:
                    if i in buy_items:
                        if not post:
                            post = True
                    #else:
                    #visited_items.add(i)
                    #recommend_list = SRRCF(session_item, item_session, visited_items, topk, i, s)
                    recommend_list, candidate_set = CRRCF(session_item, item_session, visited_items, topk, i, s, candidate_set)
                    fw.write(s + '\t' + i + '\t' + str(post) + '\t' + ('\t').join(recommend_list) + '\n')

            #update_RG(session_item, item_session, s, logs)

        fw.close()
        end_time = time.time()
        timing[topk] = end_time - start_time

    fw = codecs.open('exp_time.csv', 'w')
    for k in sorted(timing):
        fw.write('%s, %s\n' % (k, timing[k]))


def mutiply_matrices(M1, M2):
    new_M = {}
    for i in M1:
        for j in M1[i]:
            for k in M2[j]:
                if i not in new_M:
                    new_M[i] = {}

                if k not in new_M[i]:
                    new_M[i][k] = 0

                new_M[i][k] += M1[i][j]*M2[j][k]

    return new_M

def transpose(M):
    MT = {}
    for i in M:
        for j in M[i]:
            if j not in MT:
                MT[j] = {}

            MT[j][i] = M[i][j]

    return MT


def RW(II, clicked_set, top_k, target_i, candidate_set):
    recommend_items = []
    if target_i in II:
        for candidate_i in II[target_i]:
            if candidate_i not in candidate_set:
                candidate_set[candidate_i] = 0
            candidate_set[candidate_i] += II[target_i][candidate_i]

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


def recommend_RW(session_log, buy_logs, steps):
    logger = logging.getLogger('get_user_activeness')


    II  = load_graph('II.matrix')
    new_II = II
    current_steps = steps

    logger.info('Calculate transition matrix...')
    current_steps /= 2
    while current_steps > 1:
        new_II = mutiply_matrices(new_II, II)
        current_steps /= 2

    new_II_T = transpose(new_II)

    logger.info('Recommend start...')
    fw = codecs.open('step_' + str(steps) + '.txt', 'w')
    index = 0
    start_time = time.time()
    for s, logs in session_logs.items():
        index += 1
        if (index % 100000) == 0:
            print(index)

        if s in buy_logs:
            post = False
            buy_items = buy_logs[s]
            candidate_set = {}
            visited_items = set()
            for i in logs:
                if i in buy_items:
                    if not post:
                        post = True
                else:
                    visited_items.add(i)
                    recommend_list, candidate_set = RW(new_II_T, visited_items, 5, i, candidate_set)
                    fw.write(s + '\t' + i + '\t' + str(post) + '\t' + ('\t').join(recommend_list) + '\n')

    fw.close()
    end_time = time.time()
    print(end_time - start_time)




if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    buy_logs_file = '../data/yoochoose/buy_logs_4.dat'
    click_logs_file = '../data/yoochoose/click_logs_4.dat'

    print('Load logs')
    session_logs = load_raw_logs(click_logs_file, 0, 2)
    buy_logs = load_raw_logs(buy_logs_file, 0, 2)

    #recommend_CRRcf(session_logs, buy_logs)
    recommend_CRRrw(session_logs, buy_logs)
    #recommend_RW(session_logs, buy_logs, 2)

    print('EOP')


