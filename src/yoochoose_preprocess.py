import codecs
from datetime import datetime
import operator
import pickle
import logging
import time
import numpy as np


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


def extract_purchase_features(buy_logs_file, click_logs_file, output_file):
    '''
    Check did the user in a session buy something, how many times did the user click on the item
    and the index of the last view
    :param buy_logs_file:
    :param click_logs_file:
    :return output_file:
    '''
    print('load buy logs from file')
    session_index = 0
    item_index = 2
    buy_logs = {}
    index = 2
    with codecs.open(buy_logs_file, 'r') as fr:
        for row in fr:
            index += 1
            if (index % 10000) == 0:
                print(index)
            cols = row.strip().split(',')
            session_id = cols[session_index]
            item_id = cols[item_index]
            if session_id not in buy_logs:
                buy_logs[session_id] = []
            buy_logs[session_id].append(item_id)

    print('extract purchasing feature from click logs line by line')
    session_index = 0
    item_index = 2
    index = 0
    with codecs.open(click_logs_file, 'r') as fr:
        fw = codecs.open(output_file, 'w')
        session = 'NA'
        clickstream = []
        for row in fr:
            index += 1
            if (index % 10000) == 0:
                print(index)
            cols = row.strip().split(',')
            session_id = cols[session_index]
            item_id = cols[item_index]
            if session_id == session:
                clickstream.append(item_id)
            else:
                stream_size = len(clickstream)
                if session in buy_logs:
                    has_buy = 1
                    for item in buy_logs[session]:
                        view_times = 0
                        index_last_view = 0
                        for i in range(stream_size):
                            if clickstream[i] == item:
                                view_times += 1
                                index_last_view = i
                        fw.write(session + '\t' + str(has_buy) + '\t' + str(view_times) + '\t' + str(index_last_view) + '\t' + str(stream_size) + '\n')
                else:
                    has_buy = 0
                    view_times = 0
                    index_last_view = 0
                    fw.write(session + '\t' + str(has_buy) + '\t' + str(view_times) + '\t' + str(index_last_view) + '\t' + str(stream_size) + '\n')

                session = session_id
                del clickstream[:]
                clickstream.append(item_id)
        fw.close()


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


def split_logs_by_month(click_logs_file):
    '''
    split the yoochoose-clicks.dat by month
    :param click_logs_file:
    :return: the data logs of each month
    '''
    month_logs = {}
    time_index = 1
    index = 0
    with codecs.open(click_logs_file, 'r') as fw:
        for row in fw:
            index += 1
            if (index % 100000) == 0:
                print(index)

            cols = row.strip().split(',')
            split_time = cols[time_index].split('-')
            month = int(split_time[1])

            if month not in month_logs:
                month_logs[month] = []

            month_logs[month].append(row)

    for m, logs in month_logs.items():
        fw = codecs.open('../data/yoochoose/buy_logs_' + str(m) + '.dat', 'w')
        for l in logs:
            fw.write(l)
        fw.close()


def find_item_cat(input_file):
    index = 0
    item_cat = {}
    cats = [str(i) for i in range(1,13)]
    with codecs.open(input_file, 'r') as fr:
        for row in fr:
            index += 1
            if (index % 1000000) == 0:
                print(index)

            cols = row.strip().split(',')
            if cols[2] not in item_cat or (item_cat[cols[2]] != cols[3] and cols[3] in cats):
                item_cat[cols[2]] = cols[3]
            elif item_cat[cols[2]] in cats and cols[3] in cats:
                assert item_cat[cols[2]] == cols[3], 'category conflict'

    fw = codecs.open('../data/yoochoose/item_cat.txt', 'w')
    for i in item_cat:
        fw.write(i + ',' + item_cat[i] + '\n')

    fw.close()


def write_struct(W, filename):
    print('Graph storing')
    with open(filename, 'wb') as fp:
        pickle.dump(W, fp)


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

def create_II_matrix(infile):
    logger = logging.getLogger('create_II_matrix')
    si_logs = load_raw_logs(infile, 0, 2)
    is_logs = load_raw_logs(infile, 2, 0)
    SI = {}
    IS = {}
    II = {}

    logger.info('Load session logs...')
    for s, log in si_logs.items():
        degree_s = len(log)
        for i in log:
            if s not in IS:
                IS[s] = {}
            IS[s][i] = float(1 / degree_s)

    logger.info('Load item logs...')
    for i, log in is_logs.items():
        degree_i = len(log)
        for s in log:
            if i not in SI:
                SI[i] = {}
            SI[i][s] = float(1 / degree_i)

    logger.info('Create II matrix...')
    II = mutiply_matrices(SI, IS)

    logger.info('Output II matrix...')
    write_struct(II, 'II.matrix')


def export_matrix(infile):
    session_logs = load_raw_logs(infile, 0, 1)
    item_to_id = {}
    user_to_id = {}
    u_id = 0
    i_id = 0
    for u, log in session_logs.items():
        if len(log) > 2:
            user_to_id[u] = u_id
            u_id += 1

            for i in log:
                if i not in item_to_id:
                    item_to_id[i] = i_id
                    i_id += 1

    print(len(user_to_id), len(item_to_id))
    R = np.zeros((len(user_to_id), len(item_to_id)), dtype='float32')
    for u, log in session_logs.items():
        if len(log) > 2:
            u_id = user_to_id[u]
            for i in log:
                i_id = item_to_id[i]
                R[u_id][i_id] += 1

    write_struct(R, 'occur.matrix')

    fw = codecs.open('u_id.hash', 'w')
    for u in user_to_id:
        fw.write(str(u_id[u]) + '\t' + u + '\n')
    fw.close()

    fw = codecs.open('i_id.hash', 'w')
    for u in user_to_id:
        fw.write(str(u_id[u]) + '\t' + u + '\n')
    fw.close()



if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    buy_logs_file_path = '../data/yoochoose/buy_logs_4.dat'
    click_logs_file_path = '../data/CA_foursquare/conv_train.dat'
    start_time = time.time()

    export_matrix(click_logs_file_path)
    #create_II_matrix(click_logs_file_path)

    end_time = time.time()
    print("--- %s seconds ---" % (end_time - start_time))
    #extract_purchase_features(buy_logs_file_path, click_logs_file_path, 'purchase_feature.txt')
    #split_logs_by_month(buy_logs_file_path)
    #find_item_cat(click_logs_file_path)


