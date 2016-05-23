import codecs
from datetime import datetime
from numpy import histogram, arange, size, zeros
from math import sqrt, fabs, log
from scipy import stats
import pickle
import operator
import random
import matplotlib.pyplot as plt


def load_struct(filename):
    print('Load matrix')
    with open(filename, 'rb') as fp:
        W = pickle.load(fp)
    return W


def write_struct(W, filename):
    print('Graph storing')
    with open(filename, 'wb') as fp:
        pickle.dump(W, fp)


def load_stop_time(input_file, session_index, item_index, time_index):
    T = {}
    with codecs.open(input_file, 'r') as fr:
        pre_click_time = datetime.now()
        pre_click_item = '0'
        s_id = '0'
        for row in fr:
            cols = row.strip().split(',')
            if s_id != cols[session_index]:
                s_id = cols[session_index]
                pre_click_time = datetime.strptime(cols[time_index], '%Y-%m-%dT%H:%M:%S.%fZ')
                pre_click_item = cols[item_index]
                T[s_id] = {}
            else:
                post_click_time = datetime.strptime(cols[time_index], '%Y-%m-%dT%H:%M:%S.%fZ')
                if post_click_time > pre_click_time:
                    T[s_id][pre_click_item] = (post_click_time - pre_click_time).seconds
                    pre_click_item = cols[item_index]
                    pre_click_time = post_click_time
                elif post_click_time < pre_click_time:
                    raise Exception(str(pre_click_time) + '\t' + str(post_click_time) +'Time order error')
    return T



def load_raw_logs(input_file, session_index, item_index):
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


def get_item_time_dist(stop_time, item_t_dist):
    print('time distribution')
    distribution = {}
    for s in stop_time:
        for i in stop_time[s]:
            if i not in item_t_dist:
                distribution[i] = []
            distribution[i].append(stop_time[s][i])
    return distribution


def get_session_len_dist(clicks, buys, is_buy):
    len_dist = []

    if is_buy:
        for s in buys:
            len_dist.append(len(clicks[s]))
    else:
        for s in clicks:
            if s not in buys:
                len_dist.append(len(clicks[s]))

    return histogram(len_dist, bins=arange(min(len_dist), 50, 1), density=True)


def purchase_probability(click_log, buy_log):
    count_index = {}
    for s in buy_log:
        for i in buy_log[s]:
            index = click_log[s].index(i)
            if index not in count_index:
                count_index[index] = 0
            count_index[index] += 1

    total = sum(count_index.values())
    with codecs.open('tmp_exp.csv', 'w') as fw:
        for index in sorted(count_index):
            fw.write(str(index) + ',' + str(float(count_index[index] / total)) + '\n')


def purchase_hit_prob(buy_file, click_file, out_file):

    print('Load data')
    session_logs = load_raw_logs(click_file, 0, 2)
    buy_logs = load_raw_logs(buy_file, 0, 2)
    sim_matrix = load_struct('yoochoose.matrix')

    top_k = 5
    count = {}
    hit = {}
    index = 0
    for s in buy_logs:
        index += 1
        if index % 10000 == 0:
            print(index)

        clicked_set = set()
        sim_items = {}
        k = 0
        session_log = session_logs[s]
        session_log.reverse()
        for click_item in session_log:
            if click_item not in buy_logs[s]:
                if k not in count:
                    count[k] = 0
                    hit[k] = 0
                count[k] += 1
                #also-view
                sim_items = sim_matrix[click_item]
                ''' #view as a session
                sim_row = sim_matrix[click_item]
                for i in sim_row:
                    if i not in sim_items:
                        sim_items[i] = 0
                    sim_items[i] += sim_row[i]
                '''
                sorted_items = sorted(sim_items.items(), key=operator.itemgetter(1), reverse=True)

                rank = 0
                v = 0
                while rank < top_k:
                    if v == len(sorted_items):
                        break

                    if sorted_items[v][0] not in clicked_set:
                        if sorted_items[v][0] in buy_logs[s]:
                            hit[k] += 1
                            break
                        rank += 1
                    v += 1
                clicked_set.add(click_item)
                k += 1

    fw = codecs.open(out_file, 'w')
    for k in sorted(count):
        fw.write('%s,%s,%s,%s\n'%(k, count[k], hit[k], float(hit[k] / count[k])))
    fw.close()


def hash_item_by_rank(infile, outfile):
    click_log_file = infile
    hash_item_id = {}

    with codecs.open(click_log_file, 'r') as fr:
        index = 0
        for row in fr:
            index += 1
            if (index%2000000) == 0:
                print(index)

            cols = row.strip().split(',')
            if cols[0] not in hash_item_id:
                hash_item_id[cols[0]] = 0
            hash_item_id[cols[0]] += 1

    sort_items = sorted(hash_item_id.items(), key=operator.itemgetter(1), reverse=True)
    hash_items_rank = {}
    for i in range(len(sort_items)):
        hash_items_rank[sort_items[i][0]] = i

    if outfile != '':
        write_struct(hash_items_rank, 'item_id.hash')

    return hash_items_rank


def similarity_matrix_visualization(matrix_file, out_file):
    sim_matrix = load_struct(matrix_file)
    hash_item_id = hash_item_by_rank('tmp_click.csv', '')
    column_labels = range(len(hash_item_id))
    row_labels = range(len(hash_item_id))
    data = zeros(shape=(len(hash_item_id), len(hash_item_id)))

    for i in hash_item_id:
        if i in sim_matrix:
            for j in hash_item_id:
                if j in sim_matrix[i]:
                    data[hash_item_id[i]][hash_item_id[j]] = sim_matrix[i][j]

    fig, ax = plt.subplots()
    plt.matshow(data[0:50,0:50], vmin=0, vmax=1, cmap='gray_r')
    plt.colorbar()
    '''
    # put the major ticks at the middle of each cell
    ax.set_xticks(arange(data.shape[0])+0.5, minor=False)
    ax.set_yticks(arange(data.shape[1])+0.5, minor=False)

    # want a more natural, table-like display
    ax.invert_yaxis()
    ax.xaxis.tick_top()

    ax.set_xticklabels(row_labels, minor=False)
    ax.set_yticklabels(column_labels, minor=False)
    '''
    plt.savefig(out_file, format='png', dpi=1200)


if __name__ == '__main__':
    click_log_file = '../data/yoochoose/click_logs_4.dat'
    buy_log_file = '../data/yoochoose/buy_logs_4.dat'

    print('load data')
    #stop_time = load_stop_time(click_log_file, 0, 2, 1)
    #click_logs = load_raw_logs(click_log_file, 0, 2)
    #buy_logs = load_raw_logs(buy_log_file, 0, 2)
    #item_t_dist = get_item_time_dist(stop_time)
    #percentage, bin_edge = get_session_len_dist(click_logs, buy_logs, False)
    #purchase_probability(click_logs, buy_logs)
    #purchase_hit_prob(buy_log_file, click_log_file, 'good_luck.csv')
    #similarity_matrix_visualization('tmp_5100000.matrix', 'tmp_5100K.eps')

    for i in range(4900, 6000, 1000):
        similarity_matrix_visualization('tmp_%sk.matrix'%(i), 'tmp_%sk.png'%(i))

    print('EOP')