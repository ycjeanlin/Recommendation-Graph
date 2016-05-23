import codecs
import pickle
import time


def load_conv_log(input_file, session_index, item_index):
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

            session = cols[session_index]
            if session not in logs:
                logs[session] = set()

            logs[session].add(cols[item_index])

    return logs


def write_graph(part_1, part_2, filename):
    print('Graph storing')
    with open(filename + '_1', 'wb') as fp:
        pickle.dump(part_1, fp)

    with open(filename + '_2', 'wb') as fp:
        pickle.dump(part_2, fp)


if __name__ == '__main__':
    train_file = '../data/CA_foursquare/conv_train.dat'
    graph_file = 'CA_foursquare_graph'

    start_time = time.time()
    session_item = load_conv_log(train_file, 0, 1)
    item_session = load_conv_log(train_file, 1, 0)
    end_time = time.time()

    write_graph(session_item, item_session, graph_file)
    print("--- %s seconds ---" % (end_time - start_time))
