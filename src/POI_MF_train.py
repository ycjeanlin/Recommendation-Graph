import numpy as np
import codecs
import nimfa


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

    return R, user_to_id, item_to_id


def export_item_latent_matrix(item_matrix, h_iid, outfile):

    in_h_iid = {}
    for i in h_iid:
        in_h_iid[h_iid[i]] = i

    with codecs.open(outfile, 'w') as fw:
        for r in item_matrix:
            fw.write(in_h_iid[r])
            for c in item_matrix[r]:
                fw.write('\t' + str(item_matrix[r][c]))
            fw.write('\n')


if __name__ == '__main__':

    V, h_uid, h_iid = export_matrix('../data/CA_foursquare/conv_train.dat')
    #V = np.random.rand(10, 8)
    snmf = nimfa.Snmf(V, seed="random_vcol", rank=5, max_iter=12, version='r',
                      eta=1., beta=1e-4, i_conv=10, w_min_change=0)
    snmf_fit = snmf()
    item_matrix = np.transpose(snmf.coef())

    export_item_latent_matrix(item_matrix, h_iid, 'item_matrix.tsv')






