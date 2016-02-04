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


def item_based_CF(s_i_edge, i_s_edge, clicked_set, top_k, target_item):
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


def updated_item_based_CF(s_i_edge, i_s_edge, clicked_set, top_k, target_item, session_id):
    recommend_items = []
    if target_item not in i_s_edge:
        if session_id not in s_i_edge:
            s_i_edge[session_id] = set()
        i_s_edge[target_item] = set()
        s_i_edge[session_id].add(target_item)
        i_s_edge[target_item].add(session_id)
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
    if session_id not in s_i_edge:
        s_i_edge[session_id] = set()

    s_i_edge[session_id].add(target_item)
    i_s_edge[target_item].add(session_id)
    return recommend_items


def increment_item_based_CF(s_i_edge, i_s_edge, clicked_set, top_k):
    recommend_items = []
    item_score = {}
    for ci in clicked_set:
        if ci in i_s_edge:
            sessions = i_s_edge[ci]
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
                if i not in item_score:
                    item_score[i] = 0
                item_score[i] += float(pair_count[i] / speedup[degree2])

    sorted_voters = sorted(item_score.items(), key=operator.itemgetter(1), reverse=True)

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


def update_increment_item_based_CF(s_i_edge, i_s_edge, clicked_set, top_k, target_item, session_id, candidate_set):
    recommend_items = []
    if target_item not in i_s_edge:
        if session_id not in s_i_edge:
            s_i_edge[session_id] = set()
        i_s_edge[target_item] = set()
        s_i_edge[session_id].add(target_item)
        i_s_edge[target_item].add(session_id)
        return recommend_items, candidate_set


    sessions = i_s_edge[target_item]
    pair_count = {}
    for s in sessions:
        item_list = s_i_edge[s]

        for i in item_list:
            if i not in pair_count:
                pair_count[i] = 0
            pair_count[i] += 1

    degree1 = len(sessions)
    for i, count in pair_count.items():
        degree2 = len(i_s_edge[i])

        if i not in candidate_set:
            candidate_set[i] = 0
        candidate_set[i] += float(count / (degree1 + degree2 - count))

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

    if session_id not in s_i_edge:
        s_i_edge[session_id] = set()

    s_i_edge[session_id].add(target_item)
    i_s_edge[target_item].add(session_id)
    return recommend_items, candidate_set


def choose_next_node(candidates):
    return random.sample(candidates, 1)[0]


def item_based_random_walk(s_i_edge, i_s_edge, clicked_set, top_k, start_item, steps, iter):
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


def update_item_based_random_walk(s_i_edge, i_s_edge, clicked_set, top_k, start_item, session_id, steps, iter):
    recommend_items = []
    if start_item not in i_s_edge:
        if session_id not in s_i_edge:
            s_i_edge[session_id] = set()
        i_s_edge[start_item] = set()
        s_i_edge[session_id].add(start_item)
        i_s_edge[start_item].add(session_id)
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

    if session_id not in s_i_edge:
        s_i_edge[session_id] = set()

    s_i_edge[session_id].add(start_item)
    i_s_edge[start_item].add(session_id)

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


def cumulative_itemset_based_random_walk(s_i_edge, i_s_edge, clicked_set, top_k, start_item, steps, iter, candidate_set):
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


def update_cumulative_itemset_based_random_walk(s_i_edge, i_s_edge, clicked_set, top_k, start_item, session_id, steps, iter, candidate_set):
    recommend_items = []
    if start_item not in i_s_edge:
        if session_id not in s_i_edge:
            s_i_edge[session_id] = set()
        i_s_edge[start_item] = set()
        s_i_edge[session_id].add(start_item)
        i_s_edge[start_item].add(session_id)
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
    if session_id not in s_i_edge:
        s_i_edge[session_id] = set()

    s_i_edge[session_id].add(start_item)
    i_s_edge[start_item].add(session_id)

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


def write_graph(part_1, part_2, filename):
    print('Graph storing')
    with open(filename + '_1', 'wb') as fp:
        pickle.dump(part_1, fp)

    with open(filename + '_2', 'wb') as fp:
        pickle.dump(part_2, fp)


if __name__ == '__main__':
    buy_logs_file = '../data/yoochoose/buy_logs_6.dat'
    click_logs_file = '../data/yoochoose/click_logs_6.dat'

    print('Load logs')
    session_logs = load_raw_logs(click_logs_file, 0, 2)
    buy_logs = load_raw_logs(buy_logs_file, 0, 2)

    session_item = load_graph('yoochoose_graph_5_1')
    item_session = load_graph('yoochoose_graph_5_2')
    index = 0
    timing = {}
    print('Recommendation starts')
    for iteration in range(30, 210, 10):
        fw = codecs.open('RWRG_update_itemset_top_' + str(iteration) + '.txt', 'w')
        print('=============', iteration, '===============')
        print('Load graphs')
        #session_item = load_graph('yoochoose_graph_1')
        #item_session = load_graph('yoochoose_graph_2')
        index = 0
        start_time = time.time()
        for s, logs in session_logs.items():
            candidate_set = {}
            index += 1
            if (index % 100000) == 0:
                print(index)

            if s in buy_logs:
                post = False
                buy_items = buy_logs[s]
                visited_items = set()
                for i in logs:
                    if i in buy_items:
                        if not post:
                            post = True
                    else:
                        visited_items.add(i)
                        #update_cumulative_itemset_based_random_walk(s_i_edge, i_s_edge, clicked_set, top_k, start_item, session_id, steps, iter, candidate_set)
                        recommend_list, candidate_set = update_cumulative_itemset_based_random_walk(session_item, item_session, visited_items, 5, i, s, 2, iteration, candidate_set)
                        fw.write(s + '\t' + i + '\t' + str(post) + '\t' + ('\t').join(recommend_list) + '\n')

        fw.close()
        end_time = time.time()
        timing[iteration] = end_time - start_time

    fw = codecs.open('RWRG_update_itemset_top_5.csv', 'w')
    for k in sorted(timing):
        fw.write('%s, %s\n' % (k, timing[k]))

    #write_graph(session_item, item_session, 'yoochoose_graph_update')
    print('EOP')


